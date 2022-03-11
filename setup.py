# coding=utf-8

from setuptools import setup, find_packages  # type: ignore

setup(
    name='settle',
    version='0.1.0',
    packages=find_packages(),
    entry_points={'console_scripts': [
            'settle = src.client.cli:settle',
        ]
    }
)