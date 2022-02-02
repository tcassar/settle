# coding=utf-8
import sys

from crypto import hashes
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
        """Checks that _hasher is initialised correctly i.e. no strange start values"""
        h = hashes.Hasher()
        self.assertEqual(
            h.digest().int_digest(), int.from_bytes(hashlib.sha3_256(b"").digest(), byteorder=sys.byteorder)
        )  # should be initialised empty

    def test_hash(self) -> None:
        """tests that hash object can validate hash looking numbers"""
        with self.subTest("valid"):
            h_val = hashlib.sha3_256(b"1234").digest()
            h = hashes.Hash(h_val)  # create a definitely valid hash

        with self.subTest("too short"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(b'12')

        with self.subTest("too long"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(
                    b'1157920892373161954235709850086879078532699846656405640394575840079131296399360'
                )

        with self.subTest("wrong type"):
            with self.assertRaises(hashes.HashError):
                # noinspection PyTypeChecker
                hashes.Hash("dave")

    def test_update_digest(self) -> None:
        """Ensures that a hash with a given value will digest the correct thing"""
        h = hashes.Hasher(b"1234")
        h_ = hashlib.sha3_256(b"1234")

        with self.subTest("before update"):
            self.assertEqual(h.digest().h, h_.digest())

        update_msg = b"test hash update"
        h.update(update_msg)
        h_.update(update_msg)

        with self.subTest("after update"):
            self.assertEqual(h.digest().h, h_.digest())

    def test_hasher_fails(self):
        """Checks that hasher objects when not bytes are passed into it"""
        with self.assertRaises(hashes.HasherError):
            # noinspection PyTypeChecker
            hasher = hashes.Hasher("abd")
