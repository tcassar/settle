# coding=utf-8

import sys

import click
import requests

import src.client.cli_helpers as helpers
import src.crypto.keys as keys
import src.server.models as models
import src.server.schemas as schemas
import src.transactions.transaction as trn

trap = helpers.trap

###############
#  ANCILLARY  #
###############


@trap
def register(
    name,
    email,
    password,
    pub_key,
):
    """Register to settle, using email, passwd, and an RSA public key"""

    # extract and store modulus and pub exp as bytes, ready for db
    ldr = keys.RSAKeyLoader()
    try:
        ldr.load(pub_key)
        ldr.parse()
        pub_key: keys.RSAPublicKey = keys.RSAPublicKey(ldr)
    except keys.RSAParserError as rsa_err:
        click.secho(
            f"Failed to create account - issue with given RSA key;\n{rsa_err}",
            fg="red",
            bold=True,
        )
        return

    password: str = helpers.hash_password(password)
    n_as_bytes = pub_key.n.to_bytes(256, sys.byteorder)

    usr = models.User(
        name,
        email,
        hex(pub_key.n),
        hex(pub_key.e),
        password,
    )

    # build json repr of object
    schema = schemas.UserSchema()
    usr_as_json = schema.dump(usr)

    response = requests.post(helpers.url("user"), json=usr_as_json)
    try:
        helpers.validate_response(response)
    except helpers.InvalidResponseError:
        print(response)
        click.secho(f"Failed to create account under email {email}", fg="yellow")
        return

    click.secho(f"Account created successfully", fg="green")
    click.echo(f"{usr}")


@trap
def whois(email):
    """gives your name, email, public key numbers"""
    usr_response: requests.Response = requests.get(helpers.url(f"user/{email}"))
    helpers.validate_response(usr_response)

    # build a user from received data

    schema = schemas.UserSchema()
    usr = schema.load(usr_response.json())
    click.secho(f"\nFound user with email {email}:\n", fg="green")
    click.secho(str(usr))


@trap
def show(transactions, groups, email):
    """Shows all of your open transactions / groups along with IDs"""

    # note: flags are None or True for some godforsaken reason

    # show both if no flags
    if not transactions and not groups:
        transactions = groups = True

    if groups:
        click.secho("Groups that you are a member of:\n", fg="blue")

        # receive list of groups JSON;
        try:
            groups_data = requests.get(helpers.url(f"group/{email}"))
        except helpers.InvalidResponseError as ire:
            raise helpers.InvalidResponseError(f'Problem fetching your group...\n{ire}')

        group_objs: list[models.Group] = []
        for group in groups_data.json()["groups"]:
            group_objs.append(
                models.Group(group["id"], group["name"], group["password"])
            )

        groups = models.GroupList(group_objs)

        click.echo(str(groups))
        # type: ignore

    if transactions:
        click.secho("\nYour open transactions:\n", fg="blue")

        # transaction schema
        trn_schema = schemas.TransactionSchema()

        # receive list of transactions
        try:
            transactions_data = requests.get(helpers.url(f'/transaction/{email}'))
        except helpers.InvalidResponseError as ire:
            raise helpers.InvalidResponseError(f'Problem with fetching your transactions...\n{ire}')

        try:
            for transaction in transactions_data.json()["transactions"]:  # note: this may have to change
                t = trn_schema.load(transaction)
                click.secho(
                   f'{t.src} owes {t.dest} £{round(t.amount / 100, 2):02}', fg='yellow')

                click.secho(
                   f'\nReference: {t.reference}' +
                   f'\nAgreed upon at {t.time}')

        except TypeError:
            if transactions_data.json() is None:
                click.secho('No open transactions', fg='green')


@trap
def join(email, password, group_id, group_password):

    # 1: verify user
    helpers.auth_usr(email, password)

    # 2: verify group
    helpers.auth_group(group_id, group_password)

    # 3: post to groups
    group = requests.post(helpers.url(f"group/{group_id}/{email}"))
    helpers.validate_response(group)
    click.secho(f"Successfully joined group {group_id}", fg="green")


@trap
def new_group(name, password):
    schema = schemas.GroupSchema()
    # note: 0 is placeholder, will be overwritten by db
    group = models.Group(0, name, helpers.hash_password(password))

    as_json = schema.dump(group)
    response = requests.post(helpers.url("group"), json=as_json)

    try:
        helpers.validate_response(response)
    except helpers.InvalidResponseError as ire:
        raise helpers.InvalidResponseError(f'Couldn\'t create new group...\n{ire}')

    click.secho(response.text, fg="green")
    click.secho("You can join this group with `settle join`")


##############
# FUNCTIONAL #
##############

# TODO: New transaction
# TODO: new transaction
@trap
def new_transaction(email, password, dest_email, amount, group, reference):
    # 1. verify src credentials
    helpers.auth_usr(email, password)

    # 2. get users as models.User objects destination exists
    src = helpers.get_user(email)
    dest = helpers.get_user(dest_email)

    # convert amount into pence
    amount *= 100
    if type(amount) == float:
        amount //= 1
        amount = int(amount)

    # build key objects
    src_key_ldr = keys.RSAKeyLoaderFromNumbers()
    dest_key_ldr = keys.RSAKeyLoaderFromNumbers()

    src_key_ldr.load(n=int(src.modulus, 16), e=int(src.pub_exp, 16))
    dest_key_ldr.load(n=int(dest.modulus, 16), e=int(dest.pub_exp, 16))

    src_key = keys.RSAPublicKey(src_key_ldr)
    dest_key = keys.RSAPublicKey(dest_key_ldr)

    # build transaction

    transaction = trn.Transaction(
        src=src.id,
        dest=dest.id,
        amount=amount,
        src_pub=src_key,
        dest_pub=dest_key,
        msg=reference,
        group=group,
    )

    # build schema
    trn_schema = schemas.TransactionSchema()

    # post to server
    response = requests.post(
        helpers.url("transaction"), json=trn_schema.dump(transaction)
    )

    click.echo(response.text)


# TODO: simplify
@trap
def simplify(group_id):
    """Will settle the group; can be done by anyone at anytime;
    everyone signs newly generated transactions if new transactions are generated"""

    response = requests.post(helpers.url(f'/simplify/{group_id}'))

    try:
        helpers.validate_response(response)
    except helpers.InvalidResponseError as ire:
        raise helpers.InvalidResponseError(f'Problem settling group... \n{ire}')


# TODO: sign
def sign(transaction_id, key_path):
    """Signs a transaction given an ID and a path to key"""
    # load private key


# TODO: verify
def verify(groups, transactions):
    """Verifies either given transaction or a group; pass in by ID"""


# TODO: debt
def debt(email, group):
    ...
