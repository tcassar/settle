# coding=utf-8

import click
import src.crypto.hashes as hasher


@click.group()
def settle(): ...


@settle.command()
def login():
    click.echo('Username: ')
    email: str = input()
    # TODO: offload to server

    click.echo('Password: ')
    passwd: bytes = hasher.Hasher(input().encode(encoding='utf8')).digest().h
    # TODO: offload to server, wait for OKAY

    click.echo(f'{email}, {passwd!r}')
