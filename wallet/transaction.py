import json
import time
import hashlib
from wallet.keys import KeyManager

class Transaction:
    """Represents a transaction in the FBA network"""
    
    def __init__(self, from_address, to_address, amount, timestamp=None):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = float(amount)
        self.timestamp = timestamp or int(time.time())
        self.signature = None
        self.hash = None
        self.nonce = 0
        
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'from_address': self.from_address,
            'to_address': self.to_address,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash,
            'nonce': self.nonce
        }
    
    def calculate_hash(self):
        """Calculate transaction hash"""
        tx_string = f"{self.from_address}{self.to_address}{self.amount}{self.timestamp}{self.nonce}"
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def sign_transaction(self, private_key_hex):
        """Sign the transaction with private key"""
        # Calculate hash first
        self.hash = self.calculate_hash()
        
        # Sign the hash
        self.signature = KeyManager.sign_message(private_key_hex, self.hash)
        
    def verify_signature(self, public_key_hex):
        """Verify transaction signature"""
        if not self.signature or not self.hash:
            return False
        
        return KeyManager.verify_signature(public_key_hex, self.hash, self.signature)
    
    def mine_transaction(self, difficulty=4):
        """Simple proof-of-work mining for spam protection"""
        target = "0" * difficulty
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(target):
                break
            self.nonce += 1
        
        return self.hash
    
    @classmethod
    def from_dict(cls, data):
        """Create transaction from dictionary"""
        tx = cls(
            data['from_address'],
            data['to_address'],
            data['amount'],
            data['timestamp']
        )
        tx.signature = data.get('signature')
        tx.hash = data.get('hash')
        tx.nonce = data.get('nonce', 0)
        return tx
