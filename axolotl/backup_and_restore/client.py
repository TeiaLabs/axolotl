import glob
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional, TypeVar

import dotenv
import numpy as np
from bson.objectid import ObjectId
from pymilvus import Collection, connections
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
        elif isinstance(obj, np.float32):
            return obj.item()
        return super().default(obj)


def batchify_iter(
    it: Iterable[T],
    batch_size: int,
    limit: Optional[int] = -1,
) -> Iterable[list[T]]:
    """
    Iterate through sublists of size `batch_size` with a generator.

    >>> list(batchify_iter(range(1, 8), 3))
    [[1, 2, 3], [4, 5, 6], [7]]
    >>> list(batchify_iter(range(1, 8), 2))
    [[1, 2], [3, 4], [5, 6], [7]]
    """
    remaining = limit
    batch = []
    for item in it:
        batch.append(item)
        if remaining != -1:
            remaining -= 1
        if len(batch) == batch_size:
            yield batch
            batch = []
        if remaining == 0:
            break

    if batch:
        yield batch


def read_jsonl(
    path: Path,
    offset: int = 0,
    limit: int = -1,
) -> Iterable[list[dict]]:
    with path.open("r") as f:
        for _ in range(offset):
            try:
                next(f)
            except StopIteration:
                print("Offset is greater than the number of lines in the file.")
                break

        for batch in batchify_iter(f, BATCH_SIZE, limit=limit):
            batch = [line.rstrip("\n") for line in batch]
            yield list(map(json.loads, batch))


def save_jsonl(objs: Iterable, path: Path, collection_name: str):
    path.mkdir(parents=True, exist_ok=True)
    with open(f"{path}/{collection_name}.jsonl", "a") as f:
        f.write("\n".join(json.dumps(o, cls=CustomJSONEncoder) for o in objs))
        f.write("\n")


def dump_jsonl(rows: Iterator[dict], file: Path):
    with open(file, "w") as f:
        for obj in rows:
            f.write(json.dumps(obj, cls=CustomJSONEncoder) + "\n")


class BackupAndRestoreClient:
    def __init__(self, db_uir: Optional[str] = None) -> None:
        if db_uir is None:
            db_uir = os.getenv("MONGODB_URI")

        self.client = MongoClient(db_uir)

    def backup_collection(
        self,
        db: str,
        collection: str,
        path: str,
        dry_run: bool = False,
        offset: int = 0,
        limit: int = -1,
        filters: Optional[dict] = None,
    ):
        if offset < 0:
            offset = 0

        path = Path(path)
        collection = self.client[db][collection]
        if filters is None:
            filter = {}
        else:
            filter = filters

        num_docs = collection.count_documents(filter=filter)
        collection_amount = num_docs

        if not dry_run and num_docs > 0:
            print(f"Number of documents in collection: {collection_amount}.")
            if num_docs > BATCH_SIZE:
                print(f"Downloading in mini-batches of {BATCH_SIZE} documents.")
            total = 0
            if limit != -1 and limit < num_docs:
                num_docs = limit

            for i in range(0, num_docs, BATCH_SIZE):
                if total + BATCH_SIZE > num_docs:
                    l = num_docs - total
                else:
                    l = BATCH_SIZE
                documents = collection.find(filter=filter, skip=i + offset, limit=l)
                save_jsonl(documents, path, collection_name=collection.name)
                total += BATCH_SIZE
                if total > num_docs:
                    total = num_docs
                print(f"Downloaded {total}/{num_docs} documents.")
                del documents
            print(f"Saved them to '{path}'.\n")

        else:
            print(f"Number of documents in collection: {num_docs}.\n")

    def restore_collection(
        self,
        db: str,
        collection: str,
        path: str,
        dry_run: bool = False,
        offset: int = 0,
        limit: int = -1,
    ):
        path = Path(path)
        collection = self.client[db][collection]
        print(
            f"Restoring in mini-batches of {BATCH_SIZE} documents. This may take a while."
        )
        if not dry_run:
            total = 0
            for document_batch in read_jsonl(path, offset=offset, limit=limit):
                print(f"Read {len(document_batch)} documents.")

                result = collection.insert_many(document_batch)
                total += len(result.inserted_ids)
                print(f"Restored {total} documents so far.")
                del result

        else:
            print(f" Will Restore documents from '{path}'.")

    def backup_db(self, db: str, path: str, dry_run: bool = False):
        if path.endswith("/"):
            path = f"{path}{db}"
        else:
            path = f"{path}/{db}"
        if not dry_run:
            print(f"Backing up database '{db}' to '{path}'.\n")
        else:
            print(f"Will back up database '{db}' to '{path}'.\n")
        for collection in self.client[db].list_collection_names():
            print(f"Backing up collection '{collection}' to '{path}'.")
            self.backup_collection(db, collection, path, dry_run=dry_run)

    def restore_db(self, db: str, path: str, dry_run: bool = False):
        if not path.endswith("/"):
            path = f"{path}/"

        collections = glob.glob(f"{path}/*.jsonl")
        if not dry_run:
            print(f"Restoring '{path}' to database '{db}'.\n")
        else:
            print(f"Will restore '{path}' to database '{db}'.\n")
        for collection in collections:
            collection_name = Path(collection).stem
            print(f"Restoring collection '{collection}' to '{path}'.")
            self.restore_collection(
                db=db, collection=collection_name, path=collection, dry_run=dry_run
            )

    def backup_milvus_collection(
        collection_name: str,
        path: str,
        limit: int = -1,
        dry_run: bool = False,
    ):
        path = Path(path)
        connections.connect(
            alias="default",
            uri=os.environ["MILVUS_HOST"],
            password=os.getenv("MILVUS_PASSWORD", ""),
            token=os.getenv("MILVUS_TOKEN", ""),
            user=os.getenv("MILVUS_USER", ""),
        )
        collection = Collection(collection_name)
        if not dry_run:
            file = (dir / collection_name).with_suffix(".jsonl")
            if file.exists():
                print(f"File {dir / collection_name} already exists. Skipping.")
                return
            print(f"Backing up {collection_name} to {file}")
            rows = collection.query(
                "kb_name == 'sf_help'",
                limit=limit,
                output_fields=["kb_name", "pk", "vector"],
            )
            dump_jsonl(rows, file)
            print(f"Downloaded {len(rows)} documents.")
        else:
            print(f"Will back up {collection_name} to {dir / collection_name}.")
