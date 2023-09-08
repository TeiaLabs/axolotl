import os
from typing import Optional

import dotenv
import yaml
from pymongo import MongoClient

from ..backup_and_restore.client import BackupAndRestoreClient

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


def move_mongo_collection_cluster(
    origin_cluster: str,
    destination_cluster: str,
    db: str,
    destination_db: str,
    collection_name: str,
    path: str,
    dry_run: bool = False,
):
    with open(os.path.expanduser("~/.config/axolotl-clusters.yml"), "r") as file_object:
        data = yaml.load(file_object, Loader=yaml.SafeLoader)

    try:
        origin_uri = data[origin_cluster]
        destination_uri = data[destination_cluster]
    except KeyError:
        print(f"Cluster not found in axolotl-clusters config file.")
        return

    origin_client = BackupAndRestoreClient(origin_uri)
    destination_client = BackupAndRestoreClient(destination_uri)

    origin_client.backup_collection(db=db, collection=collection_name, path=path)
    path = os.path.join(path, f"{collection_name}.jsonl")
    destination_client.restore_collection(
        db=destination_db, collection=collection_name, path=path
    )


def move_mongo_db_cluster(
    origin_cluster: str,
    destination_cluster: str,
    db: str,
    path: str,
    dry_run: bool = False,
):
    with open(os.path.expanduser("~/.config/axolotl-clusters.yml"), "r") as file_object:
        data = yaml.load(file_object, Loader=yaml.SafeLoader)

    try:
        origin_uri = data[origin_cluster]
        destination_uri = data[destination_cluster]
    except KeyError:
        print(f"Cluster not found in axolotl-clusters config file.")
        return

    origin_client = BackupAndRestoreClient(origin_uri)
    destination_client = BackupAndRestoreClient(destination_uri)

    origin_client.backup_db(db, path, dry_run=dry_run)
    destination_client.restore_db(db, path, dry_run=dry_run)
