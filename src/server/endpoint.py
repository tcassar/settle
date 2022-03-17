# coding=utf-8

import os
import sqlite3

import click
from flask import Flask, g, request
from flask_restful import Resource, Api, abort  # type: ignore

from src.server import models as models
from src.server import schemas as schemas

app = Flask(__name__)
api = Api(app)

DATABASE = "/home/tcassar/projects/settle/settle_db.sqlite"

# connecting to and clearing up db


class ResourceError(Exception):
    ...


def get_db():
    """Returns current database connection"""
    db = getattr(g, "_database", None)
    if db is None:
        # connect
        db = g._database = sqlite3.connect(DATABASE)

    return db


def build_args(data_from_cursor) -> list:
    if args := data_from_cursor:
        args = [item for item in args.fetchone()]
        return args
    else:
        raise ResourceError(
            "Database error: failed to build schema of object as nothing was retrieved"
        )


@app.teardown_appcontext
def close_connection(exception):
    """Closes db if sudden error"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


class Group(Resource):
    def get(self, id: int):
        cursor = get_db().cursor()
        # check group exists and

        get_group = """SELECT * FROM groups
                 WHERE groups.id = ?"""

        try:
            group_data = cursor.execute(get_group, [id])

            # create group object
            group = models.Group(*build_args(group_data))
        except IndexError:
            abort(404, message="Group ID does not exist")
        except TypeError as te:
            abort(404, message=f"Group data invalid; {te}")

        # create group schema
        schema = schemas.GroupSchema()

        return schema.dump(group), 200

    def post(self):

        # print(request.json)
        schema = schemas.GroupSchema()
        group = schema.load(request.json)

        cursor = get_db().cursor()

        cursor.execute(
            """INSERT INTO groups (name, password) VALUES (?, ?)""",
            [group["name"], group["password"]],
        )

        get_db().commit()

        return f'Created group ID={cursor.lastrowid} named {group["name"]}', 201


class User(Resource):
    def get(self, email: str):
        # query db for all users
        cursor = get_db().cursor()

        query = """
                 SELECT users.name, users.email, keys.n, keys.e, users.password
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

        cursor = get_db().cursor()

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
        get_db().commit()

        return schema.dump(usr), 201


class UserGroupBridge(Resource):
    """For handling users connections to groups
    POST will add user to group
    GET will get all groups associated with user"""

    def post(self, id: int, email: str):
        # assumes these things already exist as they have been validated by client already
        uid_sql = """SELECT id FROM users WHERE email = ?"""

        glink_sql = """INSERT INTO group_link (group_id, usr_id) 
                        VALUES (?, ?)"""  # group id then user id

        cursor = get_db().cursor()
        uid = cursor.execute(uid_sql, [email]).fetchone()[0]

        cursor.execute(glink_sql, [id, uid])

        get_db().commit()

        glink_data = cursor.execute(
            """SELECT * from group_link WHERE id = ?""", [cursor.lastrowid]
        )

        try:
            print('making group')
            glink = models.GroupLink(*build_args(glink_data))
        except ResourceError as re:
            return 404, f'{re}, failed'

        schema = schemas.GroupLinkSchema()

        return schema.dump(glink), 201


class Transaction(Resource):
    ...


api.add_resource(Group, "/group/<int:id>", "/group")
api.add_resource(Transaction, "/transaction")
api.add_resource(User, "/user/<string:email>", "/user")
api.add_resource(UserGroupBridge, "/group/<int:id>/<string:email>")


@click.group()
def settle_server():
    ...


@click.option("-d", "--debug", is_flag=True, default=False)
@click.option("-h", "--host", default="127.0.0.1")
@settle_server.command()
def start(host, debug):
    os.chdir("/home/tcassar/projects/settle")
    app.run(debug=debug, host=host)
    db = get_db()
    cursor = db.cursor()
