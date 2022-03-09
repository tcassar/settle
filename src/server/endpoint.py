# coding=utf-8

import src.transactions.ledger as ledger

from flask import Flask, jsonify, request

app = Flask(__name__)

# load in valid ledger
ldr = ledger.LedgerLoader()
valid = ledger.Ledger(ldr.load_from_csv('./tests/test_transactions/database.csv')[0].ledger)


@app.route("/")
def hello_world():
    return "hello, world"

