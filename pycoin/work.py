import json

import asks
import henrio

from .block import Block
from .chain import PEER_NODES


async def proof_of_work(chain, last_proof):
    # Create a variable that we will use to find our next proof of work
    incrementor = last_proof + 1
    # Get start time
    # Keep incrementing the incrementor until it's equal to a number divisible by 9
    # and the proof of work of the previous block in the chain
    while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
        incrementor += 1
        # Check if any node found the solution every 60 seconds
        # If any other node got the proof, stop searching
        new_blockchain = await consensus(chain)
        if new_blockchain is not False:
            # (False:another node got proof first, new blockchain)
            return False, new_blockchain
        await henrio.sleep(60)
    # Once that number is found, we can return it as a proof of our work
    return incrementor, chain


async def consensus(blockchain):
    # Get the blocks from other nodes
    other_chains = await find_new_chains()
    # If our chain isn't longest, then we store the longest chain
    BLOCKCHAIN = blockchain
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
    # If the longest chain wasn't ours, then we set our chain to the longest
    if longest_chain == BLOCKCHAIN:
        # Keep searching for proof
        return False
    else:
        # Give up searching proof, update chain and start over again
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN


async def find_new_chains():
    # Get the blockchains of every other node
    other_chains = []
    for node_url in PEER_NODES:
        # Get their chains using a GET request
        block = await asks.get(node_url + "/blocks").content
        # Convert the JSON object to a Python dictionary
        block = Block(**json.loads(block))
        # Verify other node block is correct
        validated = validate_blockchain(block)
        if validated:
            # Add it to our list
            other_chains.append(block)
    return other_chains


def validate_blockchain(block):
    return True
