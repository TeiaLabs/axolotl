from typing import Annotated, Optional

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
    offset: Annotated[int, Option("-o", "--offset")] = 0,
    limit: Annotated[int, Option("-l", "--limit")] = -1,
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    try:
        BackupAndRestoreClient().backup_collection(
            db=db,
            collection=collection,
            path=path,
            dry_run=dryrun,
            offset=offset,
            limit=limit,
        )
        if not dryrun:
            print(f"Backed up collection '{collection}' to '{path}'.")
        else:
            print(f"Will Backup collection '{collection}' to '{path}'.")
    except Exception as e:
        print(e)


@app.command()
def restore_collection(
    db: Annotated[str, Option("-db", "--database")],
    collection: Annotated[str, Option("-c", "--collection")],
    path: Annotated[str, Option("-p", "--path")],
    offset: Annotated[int, Option("-o", "--offset")] = 0,
    limit: Annotated[int, Option("-l", "--limit")] = -1,
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    try:
        BackupAndRestoreClient().restore_collection(
            db=db,
            collection=collection,
            path=path,
            offset=offset,
            limit=limit,
            dry_run=dryrun,
        )
        if not dryrun:
            print(f"Restored collection '{collection}' to '{path}'.")
        else:
            print(f"Will Restore collection '{collection}' to '{path}'.")
    except Exception as e:
        print(e)
