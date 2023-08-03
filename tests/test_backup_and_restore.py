import os
import pytest

from pathlib import Path
from redb.core import MongoConfig, RedB
from teia_schema.instance import Instance
from pymongo import MongoClient

import dotenv
import shutil

from axolotl.backup_and_restore.client import BackupAndRestoreClient

dotenv.load_dotenv()


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
            instance = Instance(
                content=f"instance_{i}",
                kb_name="test",
                data_type="text",
            )
            try:
                instance.insert()
            except Exception as e:
                print(e)
        yield
        Instance.delete_many({})
        shutil.rmtree(Path("./tmp/"))

    def test_backup_collection(self):
        self.backup_client.backup_collection(
            db="test_db_utils",
            collection="instance",
            path="./tmp/",
            dry_run=False,
        )
        with open("./tmp/instance.jsonl") as f:
            assert len(f.readlines()) == 5
