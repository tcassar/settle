# coding=utf-8
import click


@click.command()
@click.argument('name', default='world')
def hello(name):
    """Nice greeting for you"""
    click.echo(f'hello, {name}')
