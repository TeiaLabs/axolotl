from pathlib import Path
from typing import Annotated, Optional
import json

import typer
from rich import print
from typer import Option

from axolotl import BackupAndRestoreClient

app = typer.Typer()


@app.command()
def backup_collection(
    db: Annotated[str, Option("-db", "--database")],
    collection: Annotated[str, Option("-c", "--collection")],
    path: Annotated[str, Option("-p", "--path")],
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    try:
        BackupAndRestoreClient().backup_collection(
            db=db,
            collection=collection,
            path=path,
            dry_run=dryrun,
        )
        if not dryrun:
            print(f"Backed up collection '{collection}' to '{path}'.")
        else:
            print(f"Will Backup collection '{collection}' to '{path}'.")
    except Exception as e:
        print(e)


@app.command()
def restore_collection():
    pass


@app.command()
def backup_db():
    pass


@app.command()
def restore_db():
    pass
