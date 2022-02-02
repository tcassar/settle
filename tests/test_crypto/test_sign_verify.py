# coding=utf-8

"""
Testing sign / verify through RSA working as expected
"""
import os
from unittest import TestCase


class TestRSA(TestCase):
    """Just tests RSA parts"""

    def setUpClass(cls) -> None:
        os.chdir('/home/tcassar/projects/settle/')

    def setUp(self) -> None:


    def test_encryption(self):
        ...

    def test_signing(self):
        ...
