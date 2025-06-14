import json
import time
from collections import defaultdict
from wallet.transaction import Transaction

class SimpleLedger:
    """Simple in-memory ledger for educational purposes"""
    
    def __init__(self):
        self.transactions = []
        self.balances = defaultdict(float)
        self.pending_transactions = []
        
        # Initialize with some genesis balance for demo
        self.balances['genesis'] = 1000000.0
    
    def add_transaction(self, transaction):
        """Add a validated transaction to the ledger"""
        # Validate transaction
        if not self.validate_transaction(transaction):
            raise ValueError("Invalid transaction")
        
        # Update balances
        if transaction.from_address != 'genesis':
            self.balances[transaction.from_address] -= transaction.amount
        self.balances[transaction.to_address] += transaction.amount
        
        # Add to ledger
        self.transactions.append(transaction)
        
        # Remove from pending if exists
        self.pending_transactions = [
            tx for tx in self.pending_transactions 
            if tx.hash != transaction.hash
        ]
        
        return True
    
    def add_pending_transaction(self, transaction):
        """Add transaction to pending pool"""
        if self.validate_transaction(transaction):
            self.pending_transactions.append(transaction)
            return True
        return False
    
    def validate_transaction(self, transaction):
        """Validate a transaction"""
        # Check if sender has sufficient balance (except genesis)
        if transaction.from_address != 'genesis':
            if self.balances[transaction.from_address] < transaction.amount:
                return False
        
        # Check amount is positive
        if transaction.amount <= 0:
            return False
        
        # Check hash and signature exist
        if not transaction.hash or not transaction.signature:
            return False
        
        return True
    
    def get_balance(self, address):
        """Get balance for an address"""
        return self.balances.get(address, 0.0)
    
    def get_transaction_history(self, address, limit=10):
        """Get transaction history for an address"""
        relevant_transactions = [
            tx for tx in self.transactions
            if tx.from_address == address or tx.to_address == address
        ]
        
        # Sort by timestamp (newest first)
        relevant_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return relevant_transactions[:limit]
    
    def get_pending_transactions(self):
        """Get all pending transactions"""
        return self.pending_transactions
    
    def get_all_transactions(self):
        """Get all confirmed transactions"""
        return self.transactions
    
    def get_ledger_stats(self):
        """Get ledger statistics"""
        total_supply = sum(self.balances.values())
        active_addresses = len([addr for addr, balance in self.balances.items() if balance > 0])
        
        return {
            'total_transactions': len(self.transactions),
            'pending_transactions': len(self.pending_transactions),
            'total_supply': total_supply,
            'active_addresses': active_addresses,
            'total_addresses': len(self.balances)
        }

# Global ledger instance
ledger = SimpleLedger()
