import typer

from .backup_and_restore import backup_and_restore


def main():
    app = typer.Typer()
    app.add_typer(backup_and_restore.app, name="backup-and-restore")
    app()


if __name__ == "__main__":
    main()
