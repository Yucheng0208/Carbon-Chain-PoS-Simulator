import uuid

class Wallet:
    def __init__(self, name):
        self.name = name
        self.address = str(uuid.uuid4())
        self.balance = 100
        self.stake = 0
        self.transactions = []
        self.mined_blocks = []

    def __repr__(self):
        return f"<Wallet {self.name}: {self.balance}CC, Stake: {self.stake}>"
