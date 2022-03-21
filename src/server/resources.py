# coding=utf-8

from src.server import models as models, schemas as schemas, processes as processes

from flask import request
from flask_restful import Resource, abort  # type: ignore


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
            print('not found')
            return f'User by email {email} not found', 404

        src_sql = """SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email, verified FROM transactions
                INNER JOIN pairs p on p.id = transactions.pair_id
                INNER JOIN users u on u.id = p.src_id
                INNER JOIN users u2 on u2.id = p.dest_id
                WHERE transactions.settled = 0 AND u.email = ?
        """

        dest_sql = """
        SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email, verified FROM transactions
                INNER JOIN pairs p on p.id = transactions.pair_id
                INNER JOIN users u on u.id = p.dest_id
                INNER JOIN users u2 on u2.id = p.src_id
                WHERE transactions.settled = 0 AND u.email = ?"""

        pretty_list = processes.build_transactions(src_sql, dest_sql, cursor, email)

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
            return f"Users are not both members of group {transaction.group}", 409

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

        print(
            pair_id,
            transaction.group,
            transaction.amount,
            src_key_id,
            dest_key_id,
            transaction.reference,
            transaction.time,
        )

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
        """Verify a transaction, returning copy of verified transaction"""

        try:
            processes.get_transaction_by_id(id, processes.get_db().cursor())
        except processes.ResourceNotFoundError as rnfe:
            return str(rnfe), 404


        return request.json, 200

    def patch(self, id):
        """Sign a transaction"""
        return request.json, 201


class Simplifier(Resource):
    def post(self, gid: int):
        """Actually settle the group, return img of graph, 201 if succeeded"""
        # note: will require priv key to sign all of group's outstanding transactions

        # return a ledger schema
        return request.json, 201


class GroupDebt(Resource):
    def get(self, id, email):
        """Return open transactions of a user in a group"""

        print(request.data)
