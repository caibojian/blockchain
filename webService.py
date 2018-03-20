#-*- coding:utf-8 -*-
from flask import Flask
from flask import request
import datetime as date
import json
from Block import Block

node = Flask(__name__)
# Store the transactions that
# this node has in a list
this_nodes_transactions = []

miner_address = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"
def proof_of_work(last_proof):
    # Create a variable that we will use to find
    # our next proof of work
    incrementor = last_proof + 1
    # Keep incrementing the incrementor until
    # it's equal to a number divisible by 9
    # and the proof of work of the previous
    # block in the chain
    while not(incrementor % 9 == 0 and incrementor % last_proof == 0):
        incrementor +=1
    # Once that number is found,
    # we can return it as a proof
    # of our work
    return incrementor

def create_genesis_block():
    #Manually construck a block with
    #index zero and arbitrary prebious hash
    new_block_data = {
        "proof-of-work":1,
        "transactions":None
    }
    return Block(0, date.datetime.now(), new_block_data, "0")


def next_block(last_block):
    this_index = last_block.index + 1
    this_timestamp = date.datetime.now()
    this_data = "Hey!I'm block" + str(this_index)
    this_hash = last_block.hash
    return Block(this_index, this_timestamp, this_data, this_hash)

# Create the blockchain and add the genesis block
blockchain = [create_genesis_block()]
previous_block = blockchain[0]

# Store the url data of every
# other node in the network
# so that we can communicate
# with them
peer_nodes = []
# A variable to deciding if we're mining or not
mining = True

@node.route('/txion', methods=['POST'])
def transaction():
    if request.method == 'POST':
        # On each new POST request,
        # we extract the transaction data
        new_txion = request.get_json()
        # Then we add the transaction to our list
        this_nodes_transactions.append(new_txion)
        # Because the transaction was successfully
        # submitted, we log it to our console
        print("New transaction")
        print("FROM:{}".format(new_txion['from']))
        print("TO{}".format(new_txion['to']))
        print("AMOUNT:{}\n".format(new_txion['amount']))
        return "Transaction submission successful\n"

@node.route('/mine', methods=['GET'])
def mine():
    #Get the last proof of work
    last_block = blockchain[len(blockchain)-1]
    last_proof = last_block.data['proof-of-work']
    #Find the proof of work for 
    #the current block being mined
    #Note:The program will hang here until a new proof of work is found
    proof = proof_of_work(last_proof)
    #Once we find a valid proof of work, we know we can mine a block 
    #so we reward the miner by adding a transaction
    this_nodes_transactions.append(
        {"from":"network", "to":miner_address, "amount":1}
    )
    # Now we can gather the data needed to create the new block
    new_block_data = {
        "proof-of-work":proof,
        "transactions":list(this_nodes_transactions)
    }
    new_block_index = last_block.index + 1
    new_block_timestamp = this_timestamp = date.datetime.now()
    last_block_hash = last_block.hash
    #Empty transaction list
    this_nodes_transactions[:] = []
    #Now create the new block
    mined_block = Block(
        new_block_index,
        new_block_timestamp,
        new_block_data,
        last_block_hash
    )    
    blockchain.append(mined_block)
    #Let the client know we mined a block
    return json.dumps({
        "index":new_block_index,
        "timestamp":str(new_block_timestamp),
        "data":new_block_data,
        "hash":last_block_hash
    }) + "\n"

@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain_to_send = blockchain
    #Convert our blocks into dictionaries
    #so we can send them as json objects later
    for block in chain_to_send:
        block_index = str(block.index)
        block_timestamp = str(block.timestamp)
        block_data = str(block.data)
        block_hash = block.hash
        block = {
            "index":block_index,
            "timestamp":block_timestamp,
            "data":block_data,
            "hash":block_hash
        }
        #Send our chain to whomever requested it
        chain_to_send = json.dumps(chain_to_send)
        return chain_to_send

def find_new_chains():
    #Get the blockchains of every other node
    other_chains = []
    for node_url in peer_nodes:
        #Get their chains using a GET request
        block = request.get(node_url+'/blocks').content
        #Convert the JSON object to a Python dictionary
        block = json.loads(block)
        # Add it to our list
        other_chains.append(block)
    return other_chains

def consensus():
    # Get the locks from other nodes
    other_chains = find_new_chains()
    # if our chain isn't longest,then we store the longest chain
    longest_chain = blockchain
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
        
    #if the longest chain wasn't ours,then we set our chain to the longest
    blockchain = longest_chain

node.run()