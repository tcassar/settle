# coding=utf-8
import os
from unittest import TestCase


def setUpModule():
    os.chdir("/home/tcassar/projects/settle")


class TestAncillaryCLI(TestCase):
    def test_register(self):
        ...

    def test_whois(self):
        ...

    def test_show(self):
        ...

    def test_join(self):
        ...

    def test_leave(self):
        ...

    def test_new_group(self):
        ...


class TestFunctionalCLI(TestCase):
    def test_sign(self):
        ...

    def test_verify(self):
        ...

    def test_simplify(self):
        ...

    def test_debt(self):
        ...
