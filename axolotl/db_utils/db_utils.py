from typing import Annotated, Optional

import typer
from rich import print
from typer import Option

from axolotl.db_utils.move import (
    move_mongo_collection,
    move_mongo_collection_cluster,
    move_mongo_db_cluster,
)

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


@app.command()
def move_collection_cluster(
    origin_cluster: Annotated[str, Option("-oc", "--origin-cluster")],
    destination_cluster: Annotated[str, Option("-dc", "--destination-cluster")],
    db: Annotated[str, Option("-db", "--database")],
    destination_db: Annotated[str, Option("-ddb", "--destination-database")],
    collection: Annotated[str, Option("-c", "--collection")],
    path: Annotated[str, Option("-p", "--path")],
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    move_mongo_collection_cluster(
        origin_cluster=origin_cluster,
        destination_cluster=destination_cluster,
        db=db,
        destination_db=destination_db,
        collection_name=collection,
        path=path,
        dry_run=dryrun,
    )


@app.command()
def move_db_cluster(
    origin_cluster: Annotated[str, Option("-oc", "--origin-cluster")],
    destination_cluster: Annotated[str, Option("-dc", "--destination-cluster")],
    db: Annotated[str, Option("-db", "--database")],
    path: Annotated[str, Option("-p", "--path")],
    dryrun: Annotated[bool, Option("-dryrun")] = False,
):
    move_mongo_db_cluster(
        origin_cluster=origin_cluster,
        destination_cluster=destination_cluster,
        db=db,
        path=path,
        dry_run=dryrun,
    )
