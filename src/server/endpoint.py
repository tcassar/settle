# coding=utf-8
from dataclasses import dataclass, field

import src.transactions.ledger as ledger

from flask import Flask, jsonify, request

app = Flask(__name__)

# load in valid ledger
ldr = ledger.LedgerLoader()
valid = ledger.Ledger(ldr.load_from_csv('./tests/test_transactions/database.csv')[0].ledger)


@dataclass
class Test:
    msgs: list = field(default_factory=lambda: [])

t = Test()


@app.route("/")
def greet():
    return jsonify(t)


@app.route("/", methods=['POST'])
def echo_post():
    print(request.get_json())
    t.msgs.append(request.get_json())
    return '', 204


