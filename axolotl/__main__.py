import typer

from .backup_and_restore import backup_and_restore
from .db_utils import db_utils


def main():
    app = typer.Typer()
    app.add_typer(backup_and_restore.app, name="backup-and-restore")
    app.add_typer(db_utils.app, name="db-utils")
    app()


if __name__ == "__main__":
    main()
