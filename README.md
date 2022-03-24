# Settle

App to track money between you and a group of friends.
 
## (Intended) Features
1) Custom implementation (sort of) of RSA
2) Cryptographically verified transactions so that no one can tamper with debt
5) Way to settle a groups debts in optimal no of transaction (graph simplification based on Edmonds-Karp)
4) Client side CLI
5) Database storing transactions & usr info
6) API for client server interactions


---
## Installation Guidance for Mr Clark and Others (linux)

`pip install -r requirements.txt`
`cd settle`

To install
`pip install --editable settle`

To install the server CLI
`pip install --editable settle/src/server`

To start the server
`settle-server start`
`-d` will start the server in debug
`-h` will allow you to provide an IP to host the server - see [Flask documentation](https://flask.palletsprojects.com/en/2.0.x/api/?highlight=run%20h#flask.Flask.run) for more details.

If you get an error saying that no flask app has been found
`export FLASK_APP=./src/server/endpoint.py`

---
### Absolute file paths

All of the absolute file path references are below

```
src/server/endpoint.py:41:    os.chdir("/home/tcassar/projects/settle")
src/server/processes.py:10:DATABASE = "/home/tcassar/projects/settle/settle_db.sqlite"

tests/test_crypto/test_keys.py:19:        os.chdir("/home/tcassar/projects/settle/src")
tests/test_crypto/test_sign_verify.py:15:    os.chdir("/home/tcassar/projects/settle/src")
tests/test_transactions/test_ledger.py:13:    os.chdir("/home/tcassar/projects/settle")
tests/test_transactions/test_transaction.py:11:        os.chdir("/home/tcassar/projects/settle/src")
```

These may need to be changed.
