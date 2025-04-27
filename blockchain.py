import time
import hashlib
import random
from wallet import Wallet

BLOCK_REWARD = 10
TRANSACTION_FEE = 1

def generate_hash(data):
    return hashlib.sha256(str(data).encode()).hexdigest()

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.fee = TRANSACTION_FEE
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return generate_hash(data)

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, validator):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{[t.hash for t in self.transactions]}{self.previous_hash}{self.validator}"
        return generate_hash(block_string)

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.wallets = {}

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0", "admin")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        if sender not in self.wallets or receiver not in self.wallets:
            raise ValueError("Sender or Receiver wallet not found.")

        if self.wallets[sender].balance < (amount + TRANSACTION_FEE):
            raise ValueError("Insufficient balance including transaction fee.")

        transaction = Transaction(sender, receiver, amount)
        self.wallets[sender].balance -= (amount + TRANSACTION_FEE)
        self.wallets[receiver].balance += amount
        self.wallets[sender].transactions.append(transaction)
        self.wallets[receiver].transactions.append(transaction)
        self.pending_transactions.append(transaction)

    def stake(self, wallet_address, stake_amount):
        if wallet_address in self.wallets:
            self.wallets[wallet_address].stake += stake_amount

    def select_validator(self):
        total_stake = sum(w.stake for w in self.wallets.values())
        if total_stake == 0:
            return None

        rand = random.uniform(0, total_stake)
        upto = 0
        for address, wallet in self.wallets.items():
            if upto + wallet.stake >= rand:
                return address
            upto += wallet.stake
        return None

    def mine_pending_transactions(self):
        validator = self.select_validator()
        if validator is None:
            return None

        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash,
            validator=validator
        )
        self.chain.append(block)

        for name, wallet in self.wallets.items():
            if wallet.address == validator:
                wallet.balance += BLOCK_REWARD + sum(tx.fee for tx in self.pending_transactions)
                wallet.mined_blocks.append(block.index)

        self.pending_transactions = []
        return block

    def register_wallet(self, wallet):
        self.wallets[wallet.address] = wallet
