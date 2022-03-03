# coding=utf-8

from src.transactions.transaction import Transaction

from unittest import TestCase


class TestTransactionConversion(TestCase):

    def setUp(self) -> None:

        # load transactions from file
        raw_trans = []
        with open('/home/tcassar/projects/settle/tests/test_transactions/transactions.csv') as f:
            for line in f:
                transaction = line.strip().split(',')
                raw_trans.append(transaction)

        # build into transaction objects
        transactions = []
        for src, dest, amount in raw_trans:
            trn = Transaction(int(src), int(dest), int(amount))
            transactions.append(trn)

        """ ( a, b, 10 )                    A -> B [10]
            ( a, c, 10 ) should give graph  A -> C [10]
            ( b, c ,10 )                    B -> C [10]"""

    def test_build_graph(self):
        """
        Tests that graph with right nodes from a list of transactions is built correctly
        """

    def test_build_transactions(self):
        """check that we correctly construct a list of transactions from a graph"""

