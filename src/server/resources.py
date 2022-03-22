# coding=utf-8
import json

from flask import request
from flask_restful import Resource, abort  # type: ignore

import src.transactions.transaction as transactions
import src.transactions.ledger as ledgers
from src.server import models as models, schemas as schemas, processes as processes


# Resources


class Group(Resource):
    def get(self, id: int):
        cursor = processes.get_db().cursor()
        # check group exists and
        get_group = """SELECT id, name, password FROM groups
                 WHERE groups.id = ?"""
        try:
            group_data = cursor.execute(get_group, [id])
            group_data = group_data.fetchall()
            # create group object
            group = models.Group(*processes.build_args(*group_data))
        except IndexError:
            abort(404, message="Group ID does not exist")
            group = ""  # type: ignore
        except TypeError as te:
            abort(404, message=f"Group data invalid; {te}")
            group = ""  # type: ignore
        # create group schema
        schema = schemas.GroupSchema()
        return schema.dump(group), 200

    def post(self):

        # print(request.json)
        schema = schemas.GroupSchema()
        group = schema.load(request.json)

        cursor = processes.get_db().cursor()

        cursor.execute(
            """INSERT INTO groups (name, password) VALUES (?, ?)""",
            [group.name, group.password],
        )

        processes.get_db().commit()

        return f"Created group ID={cursor.lastrowid} named {group.name}", 201


class User(Resource):
    def get(self, email: str):
        # query db for all users
        cursor = processes.get_db().cursor()

        query = """
                 SELECT users.name, users.email, keys.n, keys.e, users.password, users.id
                 FROM users, keys
                 WHERE email = ? AND keys.id = users.key_id;
                """

        # only return one usr, so unpack first into usr_data
        try:
            usr_data: list = cursor.execute(query, [email]).fetchone()
        except IndexError:
            # returned blank info
            return "User data not found", 404

        # use data to build user class
        # use schema to convert to json

        try:
            # make sure the requested user exists
            usr = models.User(*[item for item in usr_data])
            schema = schemas.UserSchema()
        except TypeError:
            # didn't have required arguments to build usr
            return "User data invalid", 404

        return schema.dump(usr), 200

    def post(self):

        cursor = processes.get_db().cursor()

        # now is a user object
        schema = schemas.UserSchema()
        usr = schema.load(request.json)

        query = """SELECT users.id FROM users WHERE email = ?
        """

        exists = cursor.execute(query, [usr.email])
        if exists.fetchall():
            abort(409, message="User already exists")

        # add user to db

        keys_query = """INSERT INTO keys (n, e)
                        VALUES (?, ?)"""

        users_query = """INSERT INTO users (NAME, EMAIL, PASSWORD, KEY_ID)
                         VALUES (?, ?, ?, ?)"""

        cursor.execute(keys_query, [usr.modulus, usr.pub_exp])

        key_id = cursor.lastrowid
        cursor.execute(users_query, [usr.name, usr.email, usr.password, key_id])
        processes.get_db().commit()

        return (schema.dump(usr),)


class UserGroupBridge(Resource):
    """For handling users connections to groups
    POST will add user to group
    GET will get all groups associated with user"""

    def post(self, id: int, email: str):
        # assumes these things already exist as they have been validated by client already
        uid_sql = """SELECT id FROM users WHERE email = ?"""

        glink_sql = """INSERT INTO group_link (group_id, usr_id) 
                        VALUES (?, ?)"""  # group id then user id

        cursor = processes.get_db().cursor()
        uid = cursor.execute(uid_sql, [email]).fetchone()[0]

        cursor.execute(glink_sql, [id, uid])

        processes.get_db().commit()

        glink_data = cursor.execute(
            """SELECT * from group_link WHERE id = ?""", [cursor.lastrowid]
        )

        try:
            print("making group")
            glink = models.GroupLink(*processes.build_args(glink_data.fetchone()))
        except processes.ResourceNotFoundError as re:
            return 404, f"{re}, failed"

        schema = schemas.GroupLinkSchema()

        return schema.dump(glink), 201

    def get(self, email: str):
        """Return all groups that a user is part of"""

        sql = """SELECT g.id, g.name, g.password FROM users
        JOIN group_link gl on users.id = gl.usr_id
        JOIN groups g on g.id = gl.group_id
        WHERE users.id
                  = (
            SELECT users.id FROM users
            WHERE email = ?
            );
        """

        cursor = processes.get_db().cursor()
        group_data = cursor.execute(sql, [email])
        groups: list[models.Group] = []

        for row in group_data.fetchall():
            groups.append(models.Group(*processes.build_args(row)))

        groups_obj = models.GroupList(groups)
        groups_schema = schemas.GroupListSchema()

        return groups_schema.dump(groups_obj), 200


class PrettyTransaction(Resource):
    def get(self, email: str):
        """Gets a user's unsigned transactions"""

        cursor = processes.get_db().cursor()

        if not processes.user_exists(email, cursor):
            print("not found")
            return f"User by email {email} not found", 404

        src_sql = """SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email FROM transactions
                INNER JOIN pairs p on p.id = transactions.pair_id
                INNER JOIN users u on u.id = p.src_id
                INNER JOIN users u2 on u2.id = p.dest_id
                WHERE transactions.src_settled = 0 AND u.email = ?
        """

        dest_sql = """
        SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email FROM transactions
                INNER JOIN pairs p on p.id = transactions.pair_id
                INNER JOIN users u on u.id = p.dest_id
                INNER JOIN users u2 on u2.id = p.src_id
                WHERE transactions.src_settled = 0 AND u.email = ?"""

        pretty_list = processes.build_pretty_transactions(
            src_sql, dest_sql, cursor, [email]
        )

        pretty_list_schema = schemas.PrettyListSchema()
        if not pretty_list:
            return "No open transactions", 200
        else:
            return pretty_list_schema.dump(pretty_list), 200

    def post(self):
        cursor = processes.get_db().cursor()

        # note: IDs are ints

        # load transaction object into schema from request
        trn_json = request.json
        trn_schema = schemas.TransactionSchema()
        transaction = trn_schema.make_transaction(trn_json)

        # check that both people involvled in transaction are members of transaction group
        sql = """SELECT count(*) FROM groups
                 INNER JOIN group_link gl on groups.id = gl.group_id
                 INNER JOIN users u
                 INNER JOIN users u2
                 WHERE group_id = ? and u.id = ? and u2.id = ?
         """

        users_in_group = cursor.execute(
            sql, [transaction.group, transaction.src, transaction.dest]
        )
        if users_in_group.fetchone()[0] == 0:
            return f"Users are not both members of group {transaction.group}", 403

        insert_to_pairs = """INSERT INTO pairs (src_id, dest_id)
                            VALUES (?, ?) ON CONFLICT DO NOTHING """

        cursor.execute(insert_to_pairs, [transaction.src, transaction.dest])
        processes.get_db().commit()

        # get relevant info
        pair_id = cursor.execute(
            """SELECT pairs.id FROM pairs 
                     WHERE src_id = ? AND dest_id = ?""",
            [transaction.src, transaction.dest],
        ).fetchone()[0]

        key_id_query = """SELECT keys.id FROM keys 
                          JOIN users u on keys.id = u.key_id
                          WHERE u.id = ?"""

        src_key_id = cursor.execute(key_id_query, [transaction.src]).fetchone()[0]
        dest_key_id = cursor.execute(key_id_query, [transaction.dest]).fetchone()[0]

        cursor.execute(
            """INSERT INTO transactions 
        (pair_id, group_id, amount, src_key, dest_key, reference, time_of_creation)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                pair_id,
                transaction.group,
                transaction.amount,
                src_key_id,
                dest_key_id,
                transaction.reference,
                transaction.time,
            ],
        )

        processes.get_db().commit()

        return cursor.lastrowid, 201


class TransactionSigVerif(Resource):
    def get(self, id):
        """Verify a transaction, returning pretty copy of verified transaction"""

        try:
            transaction = processes.get_verified_transaction_by_id(
                id, processes.get_db().cursor()
            )
        except processes.ResourceNotFoundError as rnfe:
            return str(rnfe), 404

        try:
            transaction.verify()
            verified = True
        except transactions.VerificationError:
            verified = False

        # get emails involved in transaction, check if user is src or dest
        emails = (
            processes.get_db()
            .cursor()
            .execute(
                """
                    SELECT u.email, u2.email FROM transactions 
                    JOIN pairs p on transactions.pair_id = p.id
                    JOIN users u on p.src_id = u.id
                    JOIN users u2 on dest_id = u2.id
                     WHERE transactions.id = ?
                """,
                [id],
            )
            .fetchone()
        )

        # build pretty transaction to send back to the user

        pretty = processes.transaction_to_pretty(emails, transaction, verified)

        schema = schemas.PrettyTransactionSchema()

        return schema.dump(pretty), 200

    def patch(self):
        """Append a signature to a transaction"""

        schema = schemas.SignatureSchema()
        sig = schema.make_signature(request.json)
        if request.json is None:
            return "Invalid Request", 404

        if sig.origin == "dest":
            sql = """ UPDATE transactions
                      SET dest_sig = ?
                      WHERE id = ?"""
        elif sig.origin == "src":
            sql = """UPDATE transactions
            SET src_sig = ? 
            WHERE id = ?"""
        else:
            return (
                "Signature does not originate from one of the parties in this transaction",
                403,
            )

        cursor = processes.get_db()
        cursor.execute(sql, [sig.signature, sig.transaction_id])

        processes.get_db().commit()

        return "Successfully added signature to transaction", 201


class Simplifier(Resource):
    def post(self, gid: int):
        """Actually settle the group, return ledger schema, 201 if succeeded"""

        cursor = processes.get_db()

        # build full transactions of group
        # get list of IDs required

        print(gid)

        ids = cursor.execute(
            """SELECT transactions.id from transactions
                                WHERE group_id = ? AND src_settled = 0 AND dest_settled = 0""",
            [gid],
        ).fetchall()

        unfiltered_transactions: list[transactions.Transaction] = []
        for id in ids:
            unfiltered_transactions.append(processes.get_verified_transaction_by_id(*id, cursor))  # type: ignore

        # build ledger
        ledger = ledgers.Ledger()
        for transaction in unfiltered_transactions:
            ledger.append(transaction)

        # simplify debt system
        try:
            ledger.simplify_ledger()
        except ledgers.NoFutherSimplifications:
            return (
                "No changes made to debt structure - heuristic did not find anywhere to simplify",
                202,
            )
        except ledgers.VerificationError:
            return "Couldn't simplify group - unverified transactions in group", 403

        # mark old transactions as settled

        # otherwise, group debt is now simplified
        # thus, mark off all old transactions and push in new ones
        cursor.execute(
            """UPDATE transactions 
        SET src_settled = 1, dest_settled = 1 
        WHERE group_id = ? """,
            [gid],
        )

        # push transactions to db
        for transaction in ledger.ledger:
            transaction.group = gid
            processes.push_transaction(transaction, cursor)

        return 'success', 201


class GroupDebt(Resource):
    def get(self, id):
        """Return open transactions of a user in a group"""

        cursor = processes.get_db()

        sql = """SELECT transactions.id, group_id, amount, time_of_creation, reference, u.email, u2.email
                    FROM transactions
                    INNER JOIN pairs p on p.id = transactions.pair_id
                    INNER JOIN users u on u.id = p.src_id
                    INNER JOIN users u2 on u2.id = p.dest_id
                    WHERE group_id = ? AND transactions.src_settled = 0 AND transactions.dest_settled = 0;
            """

        trns: list[models.PrettyTransaction] = []
        for row in cursor.execute(sql, [id]).fetchall():
            row = list(row)
            dest = row.pop()
            src = row.pop()
            row.append(f"{src} -> {dest}")

            pretty = models.PrettyTransaction(*processes.build_args(row), False)
            pretty = processes.verify_pretty(pretty, cursor)

            trns.append(pretty)

        schema = schemas.PrettyListSchema()
        return schema.dump(models.PrettyList(trns, [])), 200


class SignableTransaction(Resource):
    def get(self, id):
        """Returns a fully signable transaction object"""

        try:
            transaction = processes.get_verified_transaction_by_id(
                id, processes.get_db().cursor()
            )
        except processes.ResourceNotFoundError as rnfe:
            return str(rnfe), 404

        schema = schemas.TransactionSchema()
        return schema.dump(transaction), 200

    def patch(self, t_id):
        cursor = processes.get_db()
        email: dict = json.loads(request.json)['email']

        # determine if user is src or dest
        emails = cursor.execute("""SELECT u.email, u2.email FROM transactions
        JOIN pairs p on transactions.pair_id = p.id
        JOIN users u on p.src_id = u.id
        JOIN users u2 on p.dest_id = u2.id
        WHERE transactions.id = ? """, [t_id]).fetchone()

        if email == emails[0]:
            # usr is src thus append src_settled
            sql = """UPDATE transactions SET src_settled = 1 WHERE id = ?"""
        elif email == emails[1]:
            sql = """UPDATE transactions SET dest_settled = 1 WHERE id = ?"""
        else:
            return f'Email provided is not involved in transaction {t_id}', 403

        cursor.execute(sql, [t_id])
        cursor.commit()
