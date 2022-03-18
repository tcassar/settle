# coding=utf-8

import sys

import click
import requests

import src.crypto.keys as keys
import src.server.models as models
import src.server.schemas as schemas
import src.client.cli_helpers as helpers

trap = helpers.trap


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
        str(n_as_bytes),
        str(pub_key.e.to_bytes(4, sys.byteorder)),
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


# TODO: Show; change fn signature to incl email
def show(transactions, groups, email):
    """Shows all of your open transactions / groups along with IDs"""

    # note: flags are None or True for some godforsaken reason

    # show both if no flags
    if not transactions and not groups:
        transactions = groups = True

    if groups:
        click.secho('GROUPS:\n')

        # receive list of groups JSON;
        groups_data = requests.get(helpers.url(f'group/{email}'))

        print(f'received {groups_data.json()}')



# TODO: sign
def sign(transaction_id, key_path):
    """Signs a transaction given an ID and a path to key"""


# TODO: verify
def verify(groups, transactions):
    """Verifies either given transaction or a group; pass in by ID"""


# TODO: join
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


# TODO: leave
def leave(group_id):
    """If your net debt within a group is 0, you can leave a group"""


# TODO: simplify
def simplify(group_id):
    """Will settle the group; can be done by anyone at anytime;
    everyone signs newly generated transactions if new transactions are generated"""
    ...


@trap
def new_group(name, password):
    schema = schemas.GroupSchema()
    # note: 0 is placeholder, will be overwritten by db
    group = models.Group(0, name, helpers.hash_password(password))

    as_json = schema.dump(group)
    response = requests.post(helpers.url("group"), json=as_json)

    helpers.validate_response(response)

    click.secho(response.text, fg="green")
    click.secho("You can join this group with `settle join`")
