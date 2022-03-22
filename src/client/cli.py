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
@click.option("--email", prompt=True)
@settle.command()
def show(transactions, groups, email):
    """Shows all of your open transactions / groups along with IDs"""
    client.show(transactions, groups, email)


@click.option("--password", prompt=True, hide_input=True)
@click.option("--email", prompt=True)
@click.argument("key_path")
@click.argument("transaction_id")
@settle.command()
def sign(transaction_id, key_path, email, password):
    """Signs a transaction"""
    client.sign(transaction_id, key_path, email, password)


@click.option("-g", "--group", default=0)
@click.option("-t", "--transaction", default=0)
@settle.command()
def verify(group, transaction):
    """Will verify a transaction if given a transaction ID or an entire group if given a group ID"""
    client.verify(group, transaction)


@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--name", prompt=True)
@settle.command(name="new-group")
def new_group(name, password):
    client.new_group(name, password)


@click.option(
    "--group_password",
    prompt="Group Password",
    hide_input=True,
)
@click.option(
    "--password",
    prompt="Your password",
    hide_input=True,
)
@click.option("--email", prompt=True)
@click.argument("group_id")
@settle.command()
def join(email, password, group_id, group_password):
    """Joins a group given an ID"""
    client.join(email, password, group_id, group_password)


@click.option("--password", prompt="Group Password", hide_input=True)
@click.argument("group_id")
@settle.command()
def simplify(group_id, password):
    """Simplifies debt of a group"""
    client.simplify(group_id, password)


@click.option("--password", prompt=True, hide_input=True)
@click.option("--email", prompt="Your email")
@click.option("--group", "-g", prompt=True)
@click.option("--reference", prompt=True)
@click.option("--amount", prompt="Amount (in GBP)")
@click.option("--dest_email", prompt="Email of payee")
@settle.command(name="new-transaction")
def new_transaction(email, password, dest_email, amount, group, reference):
    """Generates a new transaction"""
    client.new_transaction(email, password, dest_email, amount, group, reference)


@click.option("--email", prompt=True)
@click.option("--group_id", prompt="Group ID")
@settle.command(name="show-group")
def show_group(email, group_id):
    client.group_debt(group_id, email)


@click.option("--password", prompt=True, hide_input=True)
@click.option('--email', prompt=True)
@click.argument('transaction')
@settle.command()
def tick(email, transaction, password):
    """Ticks off a transaction as settled up in the real world"""
    if transaction is None:
        click.secho('Please provide a transaction with the -t flag (--help for help)', fg='red')
        return

    client.tick(email, password, transaction)