# coding=utf-8

from src.server import schemas as schemas
from src.server import models as models


import os
import click
from flask import Flask, g
from flask_restful import Resource, Api
import sqlite3
import json

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
    def get(self, uid: int):
        # query db for all users
        cursor = get_db().cursor()

        query = """
                 SELECT users.name, users.email, keys.key_n, keys.key_e
                 FROM users, keys
                 WHERE usr_id = ? AND keys.key_id = users.key_id;
                """

        usr_data = cursor.execute(query, [uid]).fetchall()[0]

        # use data to build user class
        # use schema to convert to json

        usr = models.User(*[item for item in usr_data])
        schema = schemas.UserSchema()

        return schema.dump(usr), 200

    def post(self):
        ...


class Transaction(Resource):
    ...


api.add_resource(Group, "/group/<int:group_id>")
api.add_resource(Transaction, "/transaction")
api.add_resource(User, "/user/<int:uid>")


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
