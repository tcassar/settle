# coding=utf-8
import os

import click
from flask import Flask
from flask_restful import Resource, Api
import sqlite3

app = Flask(__name__)
api = Api(app)


class Group(Resource):
    ...


class User(Resource):
    def get(self, uid):
        # query db for all users
        return {}, 200

    def post(self):
        ...


class Transaction(Resource):
    ...


api.add_resource(Group, "/group/<int:group_id>")
api.add_resource(Transaction, "/transaction")
api.add_resource(User, "/user/<int:uid>")


@click.group()
def settle_server(): ...


@click.option('-d', '--debug', is_flag=True, default=False)
@click.option('-h', '--host', default='127.0.0.1')
@settle_server.command()
def start(host, debug):
    os.chdir('/home/tcassar/projects/settle')
    app.run(
        debug=debug,
        host=host
    )
    db = sqlite3.connect('./settle_db.sqlite')
    cursor = db.cursor()
