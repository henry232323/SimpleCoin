import hashlib
import time


class Block:
    __slots__ = ("index", "timestamp", "data", "previous", "hash")

    def __init__(self, index: int, timestamp: int, data: dict, previous_hash: bytes):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous = previous_hash

        sha = hashlib.sha256()
        sha.update("{}{}{}{}".format(self.index, self.timestamp, self.data, self.previous).encode())
        self.hash = sha.hexdigest()


def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
     and arbitrary previous hash)"""
    return Block(0, time.time(),
                 {"proof-of-work": 9, "transactions": None},
                 b"0")
