from typing import Annotated, Optional

import typer
from rich import print
from typer import Option


from axolotl.db_utils.move_collection import move_mongo_collection

app = typer.Typer()


@app.command()
def move_collection(
    db: Annotated[str, Option("-db", "--database")],
    collection: Annotated[str, Option("-c", "--collection")],
    destination_db: Annotated[str, Option("-dest", "--destination-database")],
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    try:
        move_mongo_collection(
            db=db,
            collection_name=collection,
            destination_db=destination_db,
            dry_run=dryrun,
        )
    except Exception as e:
        print(e)
