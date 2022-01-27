# coding=utf-8

"""
Unittests for crypto
Will test hashing, encrypt/decrypt, sign/verify, validity checking of keys
"""

from crypto import hashes, keys
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
        """Checks that _hasher is initialised correctly i.e. no strange start values"""
        h = hashes.Hasher()
        self.assertEqual(
            h.digest().h, hex_to_int(hashlib.sha3_256(b""))
        )  # should be initialised empty

    def test_hash(self) -> None:
        """tests that hash object can validate hash looking numbers"""
        with self.subTest("valid"):
            h_val = int(hashlib.sha3_256(b"1234").hexdigest(), 16)
            h = hashes.Hash(h_val)  # create a definitely valid hash

        with self.subTest("too short"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(12)

        with self.subTest("too long"):
            with self.assertRaises(hashes.HashError):
                hashes.Hash(
                    1157920892373161954235709850086879078532699846656405640394575840079131296399360
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
            self.assertEqual(h.digest().h, hex_to_int(h_))

        update_msg = b"test hash update"
        h.update(update_msg)
        h_.update(update_msg)

        with self.subTest("after update"):
            self.assertEqual(h.digest().h, hex_to_int(h_))

    def test_hasher_fails(self):
        """Checks that hasher objects when not bytes are passed into it"""
        with self.assertRaises(hashes.HasherError):
            # noinspection PyTypeChecker
            hasher = hashes.Hasher("abd")


class TestRSAKeyLoading(TestCase):
    """Tests for RSA Keys"""

    def test_file_loading(self):
        """Tests that file is being loaded correctly"""

        expected_start = 'modulus'
        loader = keys.RSAKeyFromFile()
        # test assumes if it starts off fine it will continue being fine
        received_start = loader.load("../crypto/sample_keys/private-key.pem")
        print(type(received_start))
        self.assertEqual(expected_start, received_start[:7])

    def test_parsing(self):
        loader = keys.RSAKeyFromFile()
        source = loader.load("../crypto/sample_keys/private-key.pem")
        loader.parse()

        # compare parsed file to known values from test keys.
        # lay out known values
        k_e = 65537

        k_d = 423186050261034755535269850442304756394425681382299639257340389895765698748645796695083715629551461265478779552919144303233011283933461726857674426838187389672166384767207640749446478175400709896956965882109510825583722503971588949457143192047749767090665830959656389449195952398626578010004019881519663179628663104934464442218001900390545484791408136305694447208476899929648797502449480345178716038904650329939041655974782350016040380747036826804133887037575013624446801222227013175622248318544806446620343545422752812273143870468255255703768242786844602119540704162618235709118874694072838664235842554512315661905
        k_n = 21616792031143752746309415579452320202510893126073087652383723408105063600070147761500936454570470862786970206983368636166003008975173251124763374054321346030354457021425165356037781636930036106404418295413726431002556836900067049867944499904312842155745102543727981913742755364262501982105715862022723433985738139067694378476466514455677010796867090616789485577458637370869261774337704654931841775536224420241750390318182742144140878560279532281843455113675020983184252503669138492451882883596202775900911000502696129433770297061845035322423193568722584809589006962060587421954603201784497846158263582144177430642603

        # build lists for testing
        cases = [
            "pub_exp",
            "priv_exp",
            "mod",
            "prime1",
            "prime2",
            "exponent1",
            "exponent2",
            "coefficient",
        ]
        known = [k_e, k_d, k_n]
        received = [
            loader.publicExponent,
            loader.privateExponent,
            loader.modulus,
            loader.prime1,
            loader.prime2,
            loader.exponent1,
            loader.exponent2,
            loader.coefficient
        ]

        for test, known_val, rec_val in zip(cases, known, received):
            with self.subTest(test):
                self.assertEqual(rec_val, known_val)
