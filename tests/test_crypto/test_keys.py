# coding=utf-8

"""
Unit tests for key handling
"""

import os
from unittest import TestCase

from src.crypto import keys


class TestRSAKeyLoading(TestCase):
    """Tests for RSA Keys"""

    def setUp(self) -> None:
        """Initialise loaders fresh between tests"""
        self.loader = keys.RSAKeyLoader()
        os.chdir("/home/tcassar/projects/settle/src")
        print(os.system("pwd"))
        self.key_path = "./crypto/sample_keys/d_private-key.pem"
        self.pub_key_path = "./crypto/sample_keys/d_public-key.pe"


    def test_file_loading(self):
        """Tests that file is being loaded correctly assuming correct file"""

        expected_start = "modulus"
        # test assumes if it starts off fine it will continue being fine
        received_start = self.loader.load(self.key_path)
        self.assertEqual(expected_start, received_start[:7])

    def test_parsing(self):
        loader = self.loader

        loader.load(self.key_path)
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

        key = keys.RSAPrivateKey(loader)

        received = [
            key.e,
            key.d,
            key.n,
            key.p,
            key.q,
            key.exp1,
            key.exp2,
            key.crt_coef,
        ]

        for test, known_val, rec_val in zip(cases, known, received):
            with self.subTest(test):
                self.assertEqual(rec_val, known_val)
                self.assertEqual(type(rec_val), type(known_val))

    def test_file_not_found(self):
        path = "./adsads"

        with self.assertRaises(keys.RSAParserError):
            loader = self.loader
            loader.load(path)

    def test_wrong_format(self):
        """Checks that we can deal with files being the wrong format"""
        with self.assertRaises(keys.RSAParserError):
            self.loader.load("./crypto/sample_keys/d_public-key.pe")

    def test_unparsed_key(self):
        """Check accessing attributes"""
        loader = self.loader
        loader.load(self.key_path)
        key = keys.RSAPrivateKey(loader)

        with self.assertRaises(keys.RSAKeyError):
            _ = key.asdf

    def test_unloaded_key(self):
        ldr = self.loader
        with self.assertRaises(keys.RSAParserError):
            ldr.parse()

    def test_public_key(self):
        ldr = self.loader
        ldr.load(self.key_path)
        ldr.parse()

        pub_key = keys.RSAPublicKey(ldr)

        with self.subTest("allowed access"):
            self.assertEqual(pub_key.e, 65537)

        with (self.subTest("deny access"), self.assertRaises(keys.RSAPublicKeyError)):
            _ = pub_key.p
