# coding=utf-8

"""
Unittests for crypto
Will test hashing, encrypt/decrypt, sign/verify, validity checking of keys
"""

from crypto import hashes
import hashlib
from unittest import TestCase


def hex_to_int(h: hashlib.sha3_256):
    """Takes hashlib generated str from hashlib.sha3_256.hexdigest() and converts to str"""
    return int(h.hexdigest(), 16)


class TestHash(TestCase):
    """
    Test hash interfaces (functionality not aim of testing as functionality comes from hashlib
    1) Check initialisation as expected
    2) Check update
    3) Check digest
    4) Check hexdigest == intdigest
    """

    def test_init(self) -> None:
        """Checks that _hasher is initialised correctly i.e. no strange start values """
        h = hashes.Hasher()
        self.assertEqual(h.digest().h, hex_to_int(hashlib.sha3_256(b'')))  # should be initialised empty

    def test_hash(self) -> None:
        """tests that hash object can validate hash looking numbers"""
        with self.subTest('valid'):
            h_val = int(hashlib.sha3_256(b'1234').hexdigest(), 16)
            h = hashes.Hash(h_val)  # create a definitely valid hash

        with self.subTest("too short"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(12)

        with self.subTest("too long"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(1157920892373161954235709850086879078532699846656405640394575840079131296399360)

        with self.subTest("wrong type"):
            with self.assertRaises(hashes.HashError):
                # noinspection PyTypeChecker
                hashes.Hash('dave')

    def test_update_digest(self) -> None:
        """Ensures that a hash with a given value will digest the correct thing"""
        h = hashes.Hasher(b'1234')
        h_ = hashlib.sha3_256(b'1234')

        with self.subTest('before update'):
            self.assertEqual(h.digest().h, hex_to_int(h_))

        update_msg = b'test hash update'
        h.update(update_msg)
        h_.update(update_msg)

        with self.subTest('after update'):
            self.assertEqual(h.digest().h, hex_to_int(h_))

    def test_hasher_fails(self):
        """Checks that hasher objects when not bytes are passed into it"""
        with self.assertRaises(hashes.HasherError):
            hasher = hashes.Hasher('abd')


class TestRSAKeyLoading(TestCase):
    """Tests for RSA Keys"""

    def test_file_loading(self):
        """Tests that file is being loaded correctly"""

        expected_start = """RSA Private-Key: (2048 bit, 2 primes)
modulus:
    "00:ab:3c:ec:18:ae:8d:f6:8c:50:2e:d7:1c:e3:37:
    "6c:ca:00:c5:e8:2a:ee:bf:9a:a5:04:79:4e:d2:b4:
    "b3:40:09:3e:38:1c:be:2d:c8:4c:27:4d:a6:40:a2:
    "d2:c3:79:a8:c4:78:68:81:39:49:a4:a7:9c:4e:eb:
    "01:4b:f3:c3:fd:53:58:cf:68:23:04:b7:b8:0d:b6:
    "b8:8c:fc:93:e7:d0:21:e3:46:c0:1c:8d:73:e4:2f:
    "cf:a8:7f:36:6f:9d:53:5c:ef:b8:46:a0:bb:32:9a:
    "c2:75:27:9e:35:74:1c:2f:95:7e:d4:e6:f7:d0:62:"""
        # test assumes if it starts off fine it will continue being fine


