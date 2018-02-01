import json
import time

import asks
import henrio

from .work import proof_of_work
from .block import Block

MINER_NODE_URL = ("http://localhost", 5000)
MINER_ADDRESS = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"


class Miner:
    def __init__(self, addr=MINER_NODE_URL):
        self.node = None
        self.addr = addr
        self.NODE_PENDING_TRANSACTIONS = None
        self.blockchain = None
        self.session = asks.Session()

    async def connect(self, timeout=None):
        self.node = await henrio.open_connection(self.addr, timeout=timeout)

    async def mine(self):
        """Mining is the only way that new coins can be created.
        In order to prevent to many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        while True:
            # Get the last proof of work
            last_block = self.blockchain[-1]
            last_proof = last_block.data['proof-of-work']
            # Find the proof of work for the current block being mined
            # Note: The program will hang here until a new proof of work is found
            proof = await proof_of_work(last_proof, self.blockchain)
            # If we didn't guess the proof, start mining again
            if not proof[0]:
                # Update blockchain and save it to file
                self.blockchain = proof[1]
                await self.node.send(json.dumps(self.blockchain))
                continue
            else:
                # Once we find a valid proof of work, we know we can mine a block so
                # we reward the miner by adding a transaction
                # First we load all pending transactions sent to the node server
                NODE_PENDING_TRANSACTIONS = await self.session.get(MINER_NODE_URL + "/tx?update=" + MINER_ADDRESS).content
                NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)
                # Then we add the mining reward
                NODE_PENDING_TRANSACTIONS.append(
                    {"from": "network",
                     "to": MINER_ADDRESS,
                     "amount": 1}
                )
                # Now we can gather the data needed to create the new block
                new_block_data = {
                    "proof-of-work": proof[0],
                    "transactions": list(NODE_PENDING_TRANSACTIONS)
                }
                new_block_index = last_block.index + 1
                new_block_timestamp = time.time()
                last_block_hash = last_block.hash
                # Empty transaction list
                self.NODE_PENDING_TRANSACTIONS.clear()
                # Now create the new block
                mined_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block_hash)
                self.blockchain.append(mined_block)
                # Let the client know this node mined a block
                await self.node.send(self.blockchain)
                await self.session.get(MINER_NODE_URL + "/blocks?update=" + MINER_ADDRESS)
