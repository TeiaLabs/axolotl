import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, TypeVar, Optional

import dotenv
from bson.objectid import ObjectId
from pymongo import MongoClient


dotenv.load_dotenv()
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 512))
T = TypeVar("T")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode("utf-8")
        return super().default(obj)


def batchify_iter(
    it: Iterable[T], batch_size: int
) -> Iterable[list[T]]:  # ta aqui o problema!!!!!!!!!!!!!!!!!!
    """
    Iterate through sublists of size `batch_size` with a generator.

    >>> list(batchify_iter(range(1, 8), 3))
    [[1, 2, 3], [4, 5, 6], [7]]
    >>> list(batchify_iter(range(1, 8), 2))
    [[1, 2], [3, 4], [5, 6], [7]]
    """
    batch = []
    for item in it:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def save_jsonl(objs: Iterable, path):
    with open(path, "a") as f:
        f.write("\n".join(json.dumps(o, cls=CustomJSONEncoder) for o in objs))
        f.write("\n")


def read_jsonl(path: Path) -> Iterable[list[dict]]:
    with path.open("r") as f:
        for batch in batchify_iter(f, BATCH_SIZE):
            batch = [line.rstrip("\n") for line in batch]
            yield list(map(json.loads, batch))


class BackupAndRestoreClient:
    def __init__(self) -> None:
        self.client = MongoClient(os.getenv("MONGODB_URI"))

    def backup_collection(
        self,
        db: str,
        collection: str,
        path: Path,
        dry_run: Optional[bool] = True,
    ):
        collection = self.client[db][collection]
        filter = {}
        num_docs = collection.count_documents(filter=filter)
        if not dry_run:
            print(f"Number of documents in collection: {num_docs}.")
            if num_docs > BATCH_SIZE:
                print(f"Downloading in mini-batches of {BATCH_SIZE} documents.")
            total = 0
            for i in range(0, num_docs, BATCH_SIZE):
                documents = collection.find(filter=filter, skip=i, limit=BATCH_SIZE)
                save_jsonl(documents, path)
                total += BATCH_SIZE
                if total > num_docs:
                    total = num_docs
                print(f"Downloaded {total}/{num_docs} documents.")
                del documents
            print(f"Saved them to '{path}'.")

        else:
            print(f"Number of documents in collection: {num_docs}.")

    def restore_collection(
        self,
        db: str,
        collection: str,
        path: Path,
        dry_run: Optional[bool] = True,
    ):
        collection = self.client[db][collection]
        print(
            f"Restoring in mini-batches of {BATCH_SIZE} documents. This may take a while."
        )
        if not dry_run:
            total = 0
            for document_batch in read_jsonl(path):
                print(f"Read {len(document_batch)} documents.")

                result = collection.insert_many(document_batch)
                total += len(result.inserted_ids)
                print(f"Restored {total} documents so far.")
                del result

        else:
            print(f" Will Restore documents from '{path}'.")

    def backup_db(self):
        pass

    def restore_db(self):
        pass
