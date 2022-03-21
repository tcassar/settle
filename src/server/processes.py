# coding=utf-8
import sqlite3

from flask import g

import src.server.models as models
import src.transactions.transaction
from src.crypto import keys as keys

DATABASE = "/home/tcassar/projects/settle/settle_db.sqlite"


class ResourceNotFoundError(Exception):
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
        raise ResourceNotFoundError(
            "Database error: failed to build schema of object as nothing was retrieved"
        )


def build_transactions(
        src_sql: str, dest_sql: str, cursor: sqlite3.Cursor, email: str
) -> models.PrettyList:
    """Returns pretty list of unchecked transactions"""
    # TODO: add transaction verification

    pretty_src_transaction_data = cursor.execute(src_sql, [email])

    src_transactions: list[models.PrettyTransaction] = []
    dest_transactions: list[models.PrettyTransaction] = []

    src_data = cursor.execute(src_sql, [email])

    for row in src_data.fetchall():
        pretty = models.PrettyTransaction(*build_args(row))
        print(f'Checking id {pretty.id}')
        verify_pretty(pretty, cursor)
        src_transactions.append(pretty)

    dest_data = cursor.execute(dest_sql, [email])

    for row in dest_data.fetchall():
        pretty = models.PrettyTransaction(*build_args(row))
        print(f'Checking id {pretty.id}')
        verify_pretty(pretty, cursor)
        dest_transactions.append(pretty)

    return models.PrettyList(src_transactions, dest_transactions)


def get_verified_transaction_by_id(
        id: int, cursor: sqlite3.Cursor
) -> src.transactions.transaction.Transaction:
    """Gets transaction object from id
    raises ResourceNotFoundError if nothing is returned"""

    sql = """SELECT src_id, dest_id, k.n, k.e, k2.n, k2.e, amount, transactions.id, reference, time_of_creation, src_sig, dest_sig, g.id FROM transactions
JOIN keys k on transactions.src_key = k.id
JOIN keys k2 on transactions.dest_key = k2.id
JOIN pairs p on transactions.pair_id = p.id
JOIN groups g on transactions.group_id = g.id
WHERE transactions.id = ?;
    """

    raw_transaction_data = cursor.execute(sql, [id]).fetchone()
    if not raw_transaction_data:
        raise ResourceNotFoundError(f"No transaction with ID={id}")

    else:
        src_key_data = raw_transaction_data[2:4]
        dest_key_data = raw_transaction_data[4:6]
        transaction_data = list(raw_transaction_data[:2]) + list(
            raw_transaction_data[6:]
        )

        (
            src_id,
            dest_id,
            amount,
            t_id,
            ref,
            time,
            src_sig,
            dest_sig,
            group,
        ) = transaction_data

        print(
            f"amount: {amount}\n"
            f"tran id: {t_id}\n"
            f"ref: {ref}\n"
            f"time: {time}\n"
            f"src_sig: {src_sig}\n"
            f"dest_sig: {dest_sig}\n"
            f"group: {group}\n"
        )

        # build keys
        # convert hex -> ints
        src_key_data = map(lambda x: int(x, 16), src_key_data)
        dest_key_data = map(lambda x: int(x, 16), dest_key_data)

        # load to key loaders
        src_ldr = keys.RSAKeyLoaderFromNumbers()
        dest_ldr = keys.RSAKeyLoaderFromNumbers()

        src_ldr.load(*src_key_data)
        dest_ldr.load(*dest_key_data)

        # add keys to transaction data in the right place so that they can be unpacked as positional arguments
        transaction_data.insert(3, dest_ldr.pub_key())
        transaction_data.insert(3, src_ldr.pub_key())

        # build signatures dict for transaction

        signatures = {}

        for sig, notary in zip([src_sig, dest_sig], [src_id, dest_id]):
            if sig:
                signatures[notary] = int(sig, 16)

        # remove signatures from transaction data, replace w dict
        transaction_data.remove(src_sig)
        transaction_data.remove(dest_sig)

        transaction_data.insert(-1, signatures)

        # return transaction
        return src.transactions.transaction.Transaction(*transaction_data)


def user_exists(email: str, cursor: sqlite3.Cursor) -> bool:
    return not not cursor.execute(
        """SELECT COUNT(*) FROM users WHERE email = ?""", [email]
    ).fetchone()[0]


def transaction_to_pretty(emails, transaction, verified):
    pretty = models.PrettyTransaction(
        transaction.ID,
        transaction.group,
        transaction.amount,
        transaction.time,
        transaction.reference,
        f"{emails[0]} -> {emails[1]}",
        verified,
    )
    return pretty


def verify_pretty(pretty: models.PrettyTransaction, cursor: sqlite3.Cursor) -> models.PrettyTransaction:
    """Update the verification status of pretty depending on signatures"""
    try:
        get_verified_transaction_by_id(pretty.id, cursor).verify()
        pretty.verified = True
    except src.transactions.transaction.VerificationError:
        pretty.verified = False
        print(f'Signature of {pretty.id} invalid')

    return pretty
