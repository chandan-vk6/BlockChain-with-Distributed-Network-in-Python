import hashlib
import uuid
import time


class BlockChain:

    def __init__(self):
        self.chain = []
        self.pending_transaction = []

        self.current_node_url = ""
        self.networknodesurl = []
        self.create_new_block(0, "0", "0" )

    def create_new_block(self, nonce, prev_block_hash, curr_block_hash):
        new_block = {
                    "index":self.chain.__len__() + 1,
                    "timestamp":time.time(),
                    "transaction": self.pending_transaction,
                    "nonce":nonce,
                    "prev_block_hash":prev_block_hash,
                    "curr_block_hash":curr_block_hash         
                     }
       
       
        self.chain.append(new_block)
        self.pending_transaction = []
       
        return new_block
    
    def get_last_block(self):
        return self.chain[self.chain.__len__() - 1]

    def make_new_transaction(self, amount, sender, recipent):
        new_transaction = {
                          "TransactionId":uuid.uuid4().hex,
                           "amount":amount,
                           "recipient":recipent,
                           "sender":sender,
                            }
       

        return new_transaction
    
    def add_pending_transaction(self, new_transaction):
         self.pending_transaction.append(new_transaction)
         return self.get_last_block()["index"] + 1
         
    
    def proof_of_work(self, prev_block_hash, curr_block_data):

        nonce = 0
        curr_block_hash = self.get_block_hash(nonce, prev_block_hash, curr_block_data) 
        while(curr_block_hash[:4] != "0000"):
            nonce += 1
            curr_block_hash = self.get_block_hash(nonce, prev_block_hash, curr_block_data) 
        
        return nonce
            
    def check_block(self, new_block ):
        if new_block.get('index') == self.get_last_block()["index"] + 1 \
                and new_block.get('prev_block_hash') == self.get_last_block()["curr_block_hash"]:
            return True
        return False   
         
    
    def get_block_hash(self, nonce, prev_block_hash, curr_block_data):

        return hashlib.sha256((str(nonce) + str(prev_block_hash) + str(curr_block_data)).encode()).hexdigest()
    
    def getblock(self, blockhash):
        found_block = None
        for block in self.chain:
            if block.get("curr_block_hash") == blockhash:
                found_block = block

        return found_block
    
    def getTransaction(self, transactionid):
        found_transaction_and_block =  None
        for block in self.chain:
            for transaction in block.get("transaction"):
                if transaction.get("TransactionId") == transactionid:
                    found_transaction_and_block = transaction
        return found_transaction_and_block
    

    def getaddress(self, address):
        
        transaction_list = []
        for block in self.chain:
            for transaction in block.get("transaction"):
                if transaction.get("sender") == address or transaction.get("recipient") == address:
                    transaction_list.append(transaction)
        
        balance = 0

        for transaction in transaction_list:
            if transaction.get("sender") == address:
                balance -= transaction.get("amount")
            elif transaction.get("recipient") == address:
                balance += transaction.get("amount")

        return {
               "transaction":transaction_list,
               "balance":balance
              }



    

    def isvalid(self, blockchain):
        valid = True
        
        for i in range(1,blockchain.__len__()):
            hash = self.get_block_hash(blockchain[i].get("nonce"), blockchain[i-1].get("curr_block_hash"),\
                                         {"transaction":blockchain[i].get("transaction"), \
                                          "index":blockchain[i].get("index")} )
                    
            if blockchain[i].get("prev_block_hash") != blockchain[i-1].get("curr_block_hash"):
                valid = False
            elif hash[:4] != "0000":
                valid = False
        
        gen_block = blockchain[0]
        if gen_block.get("nonce") != 0:
            valid = False
        elif gen_block.get("prev_block_hash") != "0":
            valid = False
        elif gen_block.get("curr_block_hash") != "0":
            valid = False
        elif gen_block.get("transaction").__len__() != 0:
            valid = False
        
        return valid
                     




    def __repr__(self):
        return {
               "chain": self.chain,
               "Pending_transaction":self.pending_transaction,
               "current_node_url":self.current_node_url,
               "network_nodes_url":self.networknodesurl
               }
    
