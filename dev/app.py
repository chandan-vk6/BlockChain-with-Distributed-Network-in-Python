from flask import Flask, request, jsonify, render_template
import requests
import os
from Blockchain import BlockChain
import uuid
import time
from flask_cors import CORS
nodeaddress = uuid.uuid4().hex
block = BlockChain()

app = Flask(__name__)
CORS(app)
    

@app.route('/')
def blockchain():
    url = request.url
    block.current_node_url = url
    return block.__repr__()

@app.route("/index", methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/mine', methods=['POST'])
def Block():
    prev_block_hash = block.get_last_block()["curr_block_hash"]
    curr_block_data  = {
        "transaction":block.pending_transaction,
        "index":block.get_last_block()["index"] + 1
    }
    print(curr_block_data)
    nonce = block.proof_of_work(prev_block_hash,curr_block_data )
    hash = block.get_block_hash(nonce, prev_block_hash, curr_block_data)

    if block.check_block({"index":block.get_last_block()["index"] + 1, \
                          "prev_block_hash": prev_block_hash}):  
        new_block =  block.create_new_block(nonce, prev_block_hash, hash)

    res = {}
    for node in block.networknodesurl:
        res = requests.post(node + "receive_new_block", json=new_block)

    if res.status_code == 200:
        reward_transaction = {"amount":15.5,
                              "sender":"00",
                              "recipient":nodeaddress}   
        res = requests.post(block.current_node_url + "transaction_and_broadcast", json=reward_transaction)

    return res.text

@app.route("/receive_new_block", methods=["POST"])
def receive_block():
    if request.method == "POST":
        data = request.get_json()
        if data and block.check_block(data):
            block.chain.append(data)
            block.pending_transaction = []
            return jsonify({"note":"Added new block succesfully"})
        else:
            return jsonify({"note":"NOt Added new block its unsuccesfull"})



@app.route('/transaction_and_broadcast', methods=['POST'])
def transcat():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            amount = data.get("amount")
            sender = data.get("sender")
            recipient = data.get("recipient")
            new_transaction = block.make_new_transaction(amount, sender, recipient)
            blockindex = block.add_pending_transaction(new_transaction)
            for nodeurl in block.networknodesurl:
                res = requests.post(nodeurl + "receive_transacation", json=data)

            return f"Transaction will be made at {blockindex} block\n"
        else:
            return f"Transaction data not found\n"

@app.route("/receive_transacation", methods=["POST"])
def receive_transaction():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            amount = data.get("amount")
            sender = data.get("sender")
            recipient = data.get("recipient")
            new_transaction = block.make_new_transaction(amount, sender, recipient)
            blockindex = block.add_pending_transaction(new_transaction)
            return f"Transaction will be made at {blockindex} block\n"
        else:
            return f"Transaction data not found\n"
    

@app.route('/brodcast_node', methods=["POST"])
def brodacast_node( ):
    if request.method == "POST":
        data = request.get_json()
        if data:
            newnodeurl = data.get("newnodeurl")
            if newnodeurl not in block.networknodesurl and newnodeurl != block.current_node_url:
                block.networknodesurl.append(newnodeurl)

            for nodeurl in block.networknodesurl:
                res = requests.post(nodeurl + "register_node" , json=data)
                
            new_networknodesurl = block.networknodesurl + [block.current_node_url]
            res =  requests.post(newnodeurl + "bulk_register", json={"networknodes":new_networknodesurl})
          
            return res.text

@app.route("/bulk_register", methods=["POST"])
def brand():
    if request.method == "POST":
        data = request.get_json()
        if data:
            networknodes = data.get("networknodes")
            for node in networknodes:
                if node not in block.networknodesurl and node != block.current_node_url:
                    block.networknodesurl.append(node)
            return jsonify({"status": "success"})


@app.route("/register_node", methods=['POST'])
def register_node():
    if request.method == "POST":
        data = request.get_json()
        if data:
            newnode = data.get("newnodeurl")
    
            if newnode not in block.networknodesurl and newnode != block.current_node_url:
                block.networknodesurl.append(newnode)
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "failed"})


@app.route("/consesus", methods=['GET'])
def consesus_block():
    
    if request.method == "GET":
        other_nodes_chains = [] 
        for node in block.networknodesurl:
            new_chain = requests.get(node)
            other_nodes_chains.append(new_chain.json())
        # print(other_nodes_chains)
        curr_maxlenchain = block.chain.__len__()
        new_maxchain = None
        new_maxpendingtransaction = None
        for chain in other_nodes_chains:
            if chain.get("chain").__len__() > curr_maxlenchain:
                curr_maxlenchain = chain.get("chain").__len__()
                new_maxchain = chain.get("chain")
                new_maxpendingtransaction = chain.get("Pending_transaction")
        print(new_maxchain)
        if new_maxchain is None or not block.isvalid(new_maxchain):
            return {
                    "note": "chain has not been replaced",
                    "chain":block.chain,
                    "transaction":block.pending_transaction
             }
        else:
            block.chain = new_maxchain
            block.pending_transaction = new_maxpendingtransaction

            return  {
                   "note": "New chain has been replaced",
                    "chain":block.chain,
                    "transaction":block.pending_transaction
               }
             

@app.route("/getblock/<blockhash>", methods=["GET"])
def getblock(blockhash):
    if request.method == "GET":
        new_block = block.getblock(blockhash)
        return new_block
        
    

@app.route("/gettransaction/<transactionid>", methods=["GET"])
def gettransactions(transactionid):
    if request.method == "GET":
        found_transaction_and_block = block.getTransaction(transactionid)
        return found_transaction_and_block
    

@app.route("/getaddress/<address>", methods=["GET"])
def get_transaction_address(address):
    if request.method == "GET":
        balance_and_address = block.getaddress(address)
        return balance_and_address
    

if __name__ == "__main__":

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)

