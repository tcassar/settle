from dataclasses import dataclass, field

from src.transactions.transaction import Transaction, LedgerBuildError


@dataclass
class Ledger:
    """Multiple transactions contained to one group (assumed from building);
    built from a stream of transaction objects"""

    # ledger, big list of transactions;
    # TODO: maybe make ledger generator
    ledger: list[Transaction] = field(default_factory=lambda: [])

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to ledger"""
        print(type(transaction))

        if type(transaction) is not Transaction:
            raise LedgerBuildError(
                f"cannot append type {transaction} to ledger; must be transaction"
            )
        else:
            self.ledger.append(transaction)

        return self.ledger

    def _verify_transactions(self):
        """Verifies the keys of all the transactions in the group.
        Raises error if a faulty transaction is found"""