# coding=utf-8
import sqlite3

from flask import g

import src.server.models as models


DATABASE = "/home/tcassar/projects/settle/settle_db.sqlite"


class ResourceError(Exception):
    ...


def get_db():
    """Returns current database connection"""
    db = getattr(g, "_database", None)
    if db is None:
        # connect
        db = g._database = sqlite3.connect(DATABASE)

    return db


def build_args(data_from_cursor: list | tuple) -> list:
    """Given a ROW OF PARAMETERS FROM DB will return list as args"""
    if args := data_from_cursor:
        args = [item for item in args]
        return args
    else:
        raise ResourceError(
            "Database error: failed to build schema of object as nothing was retrieved"
        )


def build_transactions(
    src_sql: str, dest_sql: str, cursor: sqlite3.Cursor, email: str
) -> models.PrettyList:

    pretty_src_transaction_data = cursor.execute(src_sql, [email])
    src_transactions = []
    for row in pretty_src_transaction_data:
        src_transactions.append(models.PrettyTransaction(*build_args(row)))

    pretty_dest_transaction_data = cursor.execute(dest_sql, [email])

    dest_transactions = []
    for row in pretty_dest_transaction_data:
        trn = models.PrettyTransaction(*build_args(row))
        dest_transactions.append(trn)

    return models.PrettyList(src_transactions, dest_transactions)


def user_exists(email: str, cursor: sqlite3.Cursor) -> bool:
    return not not cursor.execute("""SELECT COUNT(*) FROM users WHERE email = ?""", [email]).fetchone()[0]

