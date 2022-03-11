# coding=utf-8

from setuptools import setup

setup(
    name='Settle',
    version='0.9',
    py_modules=['client', 'crypto', 'simplify', 'transactions'],
    entry_points="""
        [console_scripts]
        hello = client.cli:hello
        """
)
