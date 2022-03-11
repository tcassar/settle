# coding=utf-8

import click
import src.crypto.hashes as hasher


@click.group()
def settle(): ...


@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--email', prompt=True)
@settle.command()
def login(email, password):

    password: bytes = hasher.Hasher(password.encode(encoding='utf8')).digest().h

    # TODO: offload both to server, wait for OKAY

    click.echo(f'{email}, {password!r}')


@settle.command()
def create_account(): ...