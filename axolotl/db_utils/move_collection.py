import os
import dotenv
from typing import Optional
from pymongo import MongoClient

dotenv.load_dotenv()
BATCH_SIZE = os.getenv("BATCH_SIZE", 512)


def move_mongo_collection(
    db: str,
    destination_db: str,
    collection_name: str,
    dry_run: bool = False,
    db_uri: Optional[str] = None,
):
    if db_uri is None:
        db_uri = os.getenv("MONGODB_URI")
    else:
        db_uri = db_uri

    client = MongoClient(db_uri)
    collection = client[db][collection_name]
    if not dry_run:
        print(
            f"Moving collection '{collection_name}' from '{db}' to '{destination_db}'."
        )
        documents = [doc for doc in collection.find()]  # TODO: add abatching
        print(f"Read {len(documents)} documents.")
        result = client[destination_db][collection_name].insert_many(documents)
        print(result.inserted_ids)
    else:
        print(
            f"Will move collection '{collection_name}' from '{db}' to '{destination_db}'."
        )
        print(f"{collection.count_documents({})} documents in collection.")
