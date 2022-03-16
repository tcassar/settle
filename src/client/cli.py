# coding=utf-8

import click
import requests

import src.crypto.hashes as hasher
import src.crypto.keys as keys
import src.server.schemas as schemas


SERVER = "http://127.0.0.1:5000/"


def url(query: str) -> str:
    return SERVER + query


def invalid_response(response: requests.Response) -> bool:
    if response.status_code == 404:
        e = response.text.strip().replace('"', '')
        click.secho(f'ERROR: {e}', fg='red')
        return True
    else:
        return False


@click.group()
def settle():
    ...


# |--------|
# |  USER  |
# |--------|


@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--email", prompt=True)
@settle.command()
def login(email, password):
    """login to settle"""
    password: bytes = hasher.Hasher(password.encode(encoding="utf8")).digest().h

    # TODO: offload both to server, wait for OKAY; if not okay, ask if account created
    # TODO: some control mechanism; make other functions only available given login
    click.secho(f"login successful for {email}", fg="green")


@click.option("--pub_key", prompt="Path to RSA key", type=click.Path())
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--email", prompt=True)
@click.option("--name", prompt="Full Name")
@settle.command()
def register(name, email, password, pub_key):
    """Register to settle, using email, passwd, and an RSA public key"""

    # extract and store modulus and pub exp as bytes, ready for db
    create = True
    ldr = keys.RSAKeyLoader()
    try:
        ldr.load(pub_key)
        ldr.parse()
        pub_key = keys.RSAPublicKey(ldr)
    except keys.RSAParserError as rsa_err:
        click.secho(
            f"Failed to create account - issue with given RSA key;\n{rsa_err}",
            fg="red",
            bold=True,
        )
        create = False

    password: bytes = hasher.Hasher(password.encode(encoding="utf8")).digest().h

    click.echo(f"{name}, {email}, {password}, {pub_key}")

    # TODO: Push info to server
    #   Check that email doesn't already exist

    if create:
        click.secho(f"Account created successfully, using email {email}", fg="green")
    else:
        click.secho(f"Account could not be created")


@click.argument('email')
@settle.command()
def whois(email):
    """gives your name, email, public key numbers"""
    usr_response: requests.Response = requests.get(url(f'/user/{email}'))
    if invalid_response(usr_response):
        return

    # build a user from received data

    schema = schemas.UserSchema()
    usr = schema.load(usr_response.json())

    click.secho(str(usr), fg='green')



@click.option('-g', '--groups', flag_value='groups', default=False)
@click.option('-t', '--transactions', flag_value='transactions', default=False)
@settle.command()
def show(transactions, groups):
    """Shows all of your open transactions / groups along with IDs"""

    # note: flags are None or True for some godforsaken reason

    # show both if no flags
    if not transactions and not groups:
        transactions = groups = True

    click.echo(f'{transactions}, {groups}')

# |----------------|
# |  TRANSACTIONS  |
# |----------------|


@click.argument('key_path')
@click.argument('transaction_id')
@settle.command()
def sign(transaction_id, key_path):
    """Signs a transaction given an ID and a path to key"""


@click.option('-g', '--groups', flag_value='groups', default=False)
@click.option('-t', '--transactions', flag_value='transactions', default=False)
@settle.command()
def verify(groups, transactions):
    """Verifies either given transaction or a group; pass in by ID"""


# |----------|
# |  GROUPS  |
# |----------|

@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.argument('group_id')
@settle.command()
def join(password, group_id):
    ...


@click.argument('group_id')
@settle.command()
def leave(group_id):
    """If your net debt within a group is 0, you can leave a group"""


@click.argument('group_id')
@settle.command()
def simplify(group_id):
    """Will settle the group; can be done by anyone at anytime;
    everyone signs newly generated transactions if new transactions are generated"""
    ...


# |-----------|
# |  GENERAL  |
# |-----------|

# TODO: specify group or trn, show by id

@click.option('-g', '--groups', flag_value='groups', default=False)
@click.option('-t', '--transactions', flag_value='transactions', default=False)
@settle.command()
def new(groups, transactions):
    """generate a new transaction or group"""
    if groups and transactions:
        click.secho(f'Cannot handle both new group and new transaction; one at a time please', fg='yellow')


@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def new_group(password):
    ...

