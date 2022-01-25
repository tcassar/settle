# coding=utf-8

"""
Unittests for crypto
Will test hashing, encrypt/decrypt, sign/verify, validity checking of keys
"""

from crypto import rsa
import hashlib
from unittest import TestCase


class TestHash(TestCase):
    """
    Test hash interfaces (functionality not aim of testing as functionality comes from hashlib
    1) Check initialisation as expected
    2) Check update
    3) Check digest
    4) Check hexdigest == intdigest
    """

    def test_init(self) -> None:
        """Checks that hasher is initialised correctly i.e. no strange start values """
        h = rsa.Hasher()
        self.assertEqual(h.digest(), hashlib.sha256(b'').hexdigest())  # should be initialised empty

    def test_hash(self) -> None:
        """tests that hash object can validate hash looking numbers"""
        with self.subTest('valid'):
            h_val = int(hashlib.sha3_256(b'1234').hexdigest(), 16)
            h = rsa.Hash(h_val)  # create a definitely valid hash

        with self.subTest("too short"):
            with self.assertRaises(rsa.HashError):
                h = rsa.Hash(12)

        with self.subTest("too long"):
            with self.assertRaises(rsa.HashError):
                h = rsa.Hash(1157920892373161954235709850086879078532699846656405640394575840079131296399360)

        with self.subTest("wrong type"):
            with self.assertRaises(rsa.HashError):
                h = rsa.Hash('dave')




    def test_update_digest(self) -> None:
        """Ensures that a hash with a given value will digest the correct thing"""
        h = rsa.Hasher(b'1234')
        h_ = hashlib.sha3_256(b'1234')

        with self.subTest('before update'):
            self.assertEqual(h.digest(), h_.hexdigest())

        update_msg = b'test hash update'
        h.update(update_msg)
        h_.update(update_msg)

        with self.subTest('after update'):
            self.assertEqual(h.digest(), h_.hexdigest())








