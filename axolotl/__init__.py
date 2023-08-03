import logging

import dotenv

dotenv.load_dotenv()
logging.basicConfig(level=logging.CRITICAL)  # here to prevent log.WARN clutter

from .backup_and_restore.client import BackupAndRestoreClient

__all__ = ["BackupAndRestoreClient"]
