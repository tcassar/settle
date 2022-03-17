# coding=utf-8

import click

import src.client.client as client


@click.group()
def settle():
    ...


# |--------|
# |  USER  |
# |--------|


@click.option("--pub_key", prompt="Path to RSA key", type=click.Path())
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--email", prompt=True)
@click.option("--name", prompt="Full Name")
@settle.command()
def register(
    name,
    email,
    password,
    pub_key,
):
    client.register(name, email, password, pub_key)


@click.argument("email")
@settle.command()
def whois(email):
    client.whois(email)


@click.option("-g", "--groups", flag_value="groups", default=False)
@click.option("-t", "--transactions", flag_value="transactions", default=False)
@settle.command()
def show(transactions, groups):
    """Shows all of your open transactions / groups along with IDs"""
    client.show(transactions, groups)


@click.argument("key_path")
@click.argument("transaction_id")
@settle.command()
def sign(transaction_id, key_path):

    client.sign(transaction_id, key_path)


@click.option("-g", "--groups", flag_value="groups", default=False)
@click.option("-t", "--transactions", flag_value="transactions", default=False)
@settle.command()
def verify(groups, transactions):
    client.verify(groups, transactions)


@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--name", prompt=True)
@settle.command(name="new-group")
def new_group(name, password):
    client.new_group(name, password)


#
# @click.option(
#     "--group_password",
#     prompt="Group Password",
#     hide_input=True,
# )
# @click.option(
#     "--password",
#     prompt="Your password",
#     hide_input=True,
# )
# @click.option("--email", prompt=True)
# @click.argument("group_id")
# @settle.command()
# def join(email, password, group_id, group_password):


@settle.command()
def join():
    email = "cassar.thomas.e@gmail.com"
    password = "admin"
    group_id = 3
    group_password = "test"

    client.join(email, password, group_id, group_password)


@click.argument("group_id")
@settle.command()
def leave(group_id):
    client.leave(group_id)


@click.argument("group_id")
@settle.command()
def simplify(group_id):
    client.simplify(group_id)
