# coding=utf-8

import click
import src.crypto.hashes as hasher
import src.crypto.keys as keys


@click.group()
def settle(): ...


@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--email', prompt=True)
@settle.command()
def login(email, password):

    password: bytes = hasher.Hasher(password.encode(encoding='utf8')).digest().h

    # TODO: offload both to server, wait for OKAY; if not okay, ask if account created
    # TODO: some control mechanism; make other functions only available given login
    click.secho(f'login successful for {email}', fg='green')


@click.option('--pub_key', prompt='Path to RSA key')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--email', prompt=True)
@click.option('--name', prompt='Full Name')
@settle.command()
def register(name, email, password, pub_key):
    # extract and store modulus and pub exp as bytes, ready for db
    create = True
    ldr = keys.RSAKeyLoader()
    try:
        ldr.load(pub_key)
        ldr.parse()
        pub_key = keys.RSAPublicKey(ldr)
    except keys.RSAParserError as rsa_err:
        click.secho(f'Failed to create account - issue with given RSA key;\n{rsa_err}', fg='red', bold=True)
        create = False

    password: bytes = hasher.Hasher(password.encode(encoding='utf8')).digest().h

    click.echo(f'{name}, {email}, {password}, {pub_key}')

    # TODO: Push info to server
    #   Check that email doesn't already exist

    if create:
        click.secho(f'Account created successfully, using email {email}', fg='green')
    else:
        click.secho(f'Account could not be created')
