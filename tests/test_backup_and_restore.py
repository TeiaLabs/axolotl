import os
import shutil
from pathlib import Path
from typing import Optional

import dotenv
import pytest
from pymongo import MongoClient
from redb.core import Document, MongoConfig, RedB

from axolotl.backup_and_restore.client import BackupAndRestoreClient


dotenv.load_dotenv()


class Dog(Document):
    name: str
    age: int
    breed: str
    color: str
    is_good_boy: bool
    is_pet: Optional[bool] = None

    @classmethod
    def get_hashable_fields(cls):
        return [cls.name, cls.breed]

    def __eq__(self, other: "Dog") -> bool:
        if isinstance(other, Dog):
            b = other.dict()
        elif isinstance(other, dict):
            b = other
        else:
            return False
        a = self.dict()
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        assert a_keys == b_keys
        # Iterating is better than just "=="
        # in case of an error the log will be more readable :3
        for a_key in a_keys:
            if a_key != "updated_at":
                assert a[a_key] == b[a_key]
        return True


class TestBackupAndRestore:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        RedB.setup(
            MongoConfig(
                database_uri=os.getenv("MONGODB_URI"),
                default_database="test_db_utils",
            )
        )

    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.backup_client = BackupAndRestoreClient()

    @pytest.fixture(autouse=True)
    def setup_instances(self):
        for i in range(5):
            instance = Dog(
                name=f"instance_{i}",
                age=i,
                color="black",
                breed="axolotl",
                is_good_boy=True,
            )
            try:
                instance.insert()
            except Exception as e:
                print(e)
        yield
        Dog.delete_many({})
        shutil.rmtree(Path("./tmp/"))

    def test_backup_collection(self):
        self.backup_client.backup_collection(
            db="test_db_utils",
            collection="dog",
            path="./tmp/",
            dry_run=False,
        )
        with open("./tmp/dog.jsonl") as f:
            assert len(f.readlines()) == 5

    def test_restore_collection(self):
        self.backup_client.backup_collection(
            db="test_db_utils",
            collection="dog",
            path="./tmp/",
            dry_run=False,
        )
        Dog.delete_many({})
        self.backup_client.restore_collection(
            db="test_db_utils",
            collection="dog",
            path="./tmp/dog.jsonl",
            dry_run=False,
        )
        assert len(Dog.find_many()) == 5
