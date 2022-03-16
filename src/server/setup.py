# coding=utf-8
from setuptools import setup, find_packages  # type: ignore

setup(
    name='settle-server',
    version='0.1.0',
    py_modules=['endpoint'],
    entry_points='''
    [console_scripts]
    settle-server=endpoint:settle_server
    '''
)