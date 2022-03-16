# coding=utf-8

from src.server import models as models
from src.server import schemas as schemas

import click
from flask import Flask, g, request
from flask_restful import Resource, Api, abort
import os
import sqlite3


app = Flask(__name__)
api = Api(app)

DATABASE = "/home/tcassar/projects/settle/settle_db.sqlite"

# connecting to and clearing up db


def get_db():
    """Returns current database connection"""
    db = getattr(g, "_database", None)
    if db is None:
        # connect
        db = g._database = sqlite3.connect(DATABASE)

    return db


@app.teardown_appcontext
def close_connection(exception):
    """Closes db if sudden error"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


class Group(Resource):
    ...


class User(Resource):
    
    def get(self, email: str):
        # query db for all users
        cursor = get_db().cursor()

        query = """
                 SELECT users.name, users.email, keys.n, keys.e
                 FROM users, keys
                 WHERE email = ? AND keys.key_id = users.key_id;
                """

        # only return one usr, so unpack row into usr_data
        try:
            usr_data: list = cursor.execute(query, [email]).fetchall()[0]
        except IndexError:
            # returned blank info
            return 'User data not found', 404

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

        print(usr)
        print(usr.password)

        # add user to db

        keys_query = """INSERT INTO keys (n, e)
                        VALUES (?, ?)"""

        users_query = """INSERT INTO users (NAME, EMAIL, PASSWORD, KEY_ID)
                         VALUES (?, ?, ?, ?)"""

        cursor.execute(keys_query, [usr.modulus, usr.pub_exp])

        key_id = cursor.lastrowid
        cursor.execute(users_query, [usr.name, usr.email, usr.password, key_id])
        get_db().commit()


class Transaction(Resource):
    ...


api.add_resource(Group, "/group/<int:group_id>")
api.add_resource(Transaction, "/transaction")
api.add_resource(User, "/user/<string:email>", "/user")


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
