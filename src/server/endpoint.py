# coding=utf-8
import os

import click
from flask import Flask, g
from flask_restful import Resource, Api, abort  # type: ignore

from src.server.processes import get_db
from src.server.resources import (
    Group,
    User,
    UserGroupBridge,
    PrettyTransaction,
    TransactionSigVerif,
    Simplifier,
    GroupDebt,
    SignableTransaction,
)

app = Flask(__name__)
api = Api(app)


@app.teardown_appcontext
def close_connection(exception):
    """Closes db if sudden error"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


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


api.add_resource(Group, "/group/<int:id>", "/group")

api.add_resource(PrettyTransaction, "/transaction", "/transaction/<string:email>")

api.add_resource(User, "/user/<string:email>", "/user")

api.add_resource(
    UserGroupBridge, "/group/<int:id>/<string:email>", "/group/<string:email>"
)

api.add_resource(
    TransactionSigVerif, "/transaction/auth/<int:id>", "/transaction/auth/"
)

api.add_resource(Simplifier, "/simplify/<int:gid>")

api.add_resource(GroupDebt, "/group/debt/<int:id>")

api.add_resource(SignableTransaction, "/transaction/signable/<int:id>")
