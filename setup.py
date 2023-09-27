# coding=utf-8

from setuptools import setup, find_packages  # type: ignore

DEPENDENCIES = setup_requires = [
    "Click==8.1.3",
    "graphviz",
    "marshmallow",
    "flask",
    "flask_restful",
    "ordered_set",
    "requests",
]

setup(
    name="settle",
    version="0.1.0",
    packages=find_packages(),
    setup_requires=DEPENDENCIES,
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "settle = src.client.cli:settle",
            "settle-server = src.server.endpoint:settle_server",
        ]
    },
)
