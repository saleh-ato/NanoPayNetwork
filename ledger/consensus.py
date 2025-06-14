import time
import random
from collections import defaultdict

class FBAConsensus:
    """Educational FBA consensus simulation"""
    
    def __init__(self):
        self.nodes = {}  # node_id -> node_info
        self.quorum_slices = {}  # node_id -> list of trusted nodes
        self.votes = defaultdict(dict)  # transaction_hash -> node_id -> vote
        self.consensus_results = {}  # transaction_hash -> result
        
        # Initialize some mock nodes for demonstration
        self.initialize_mock_nodes()
    
    def initialize_mock_nodes(self):
        """Initialize mock nodes for demonstration"""
        mock_nodes = [
            {'id': 'node_1', 'name': 'FBA Node 1', 'stake': 100},
            {'id': 'node_2', 'name': 'FBA Node 2', 'stake': 80},
            {'id': 'node_3', 'name': 'FBA Node 3', 'stake': 90},
            {'id': 'node_4', 'name': 'FBA Node 4', 'stake': 70},
            {'id': 'node_5', 'name': 'FBA Node 5', 'stake': 85}
        ]
        
        for node in mock_nodes:
            self.nodes[node['id']] = node
        
        # Set up quorum slices (each node trusts 3-4 others)
        self.quorum_slices = {
            'node_1': ['node_2', 'node_3', 'node_4'],
            'node_2': ['node_1', 'node_3', 'node_5'],
            'node_3': ['node_1', 'node_2', 'node_4', 'node_5'],
            'node_4': ['node_1', 'node_3', 'node_5'],
            'node_5': ['node_2', 'node_3', 'node_4']
        }
    
    def simulate_vote(self, transaction_hash):
        """Simulate voting process for a transaction"""
        # Each node votes with some probability
        for node_id in self.nodes:
            if random.random() > 0.1:  # 90% chance to vote
                vote = random.choice(['accept', 'reject']) if random.random() > 0.8 else 'accept'
                self.votes[transaction_hash][node_id] = {
                    'vote': vote,
                    'timestamp': int(time.time()),
                    'node_name': self.nodes[node_id]['name']
                }
    
    def check_consensus(self, transaction_hash):
        """Check if consensus is reached for a transaction"""
        if transaction_hash not in self.votes:
            return None
        
        votes = self.votes[transaction_hash]
        total_nodes = len(self.nodes)
        accept_votes = sum(1 for v in votes.values() if v['vote'] == 'accept')
        reject_votes = sum(1 for v in votes.values() if v['vote'] == 'reject')
        
        # Simple consensus: need 2/3 majority
        threshold = (2 * total_nodes) // 3
        
        if accept_votes >= threshold:
            result = 'consensus_accept'
        elif reject_votes >= threshold:
            result = 'consensus_reject'
        else:
            result = 'pending'
        
        self.consensus_results[transaction_hash] = {
            'result': result,
            'accept_votes': accept_votes,
            'reject_votes': reject_votes,
            'total_votes': len(votes),
            'threshold': threshold,
            'timestamp': int(time.time())
        }
        
        return result
    
    def get_consensus_status(self, transaction_hash):
        """Get consensus status for a transaction"""
        if transaction_hash in self.consensus_results:
            return self.consensus_results[transaction_hash]
        
        if transaction_hash in self.votes:
            # Calculate current status
            self.check_consensus(transaction_hash)
            return self.consensus_results.get(transaction_hash)
        
        return None
    
    def get_node_votes(self, transaction_hash):
        """Get all node votes for a transaction"""
        return self.votes.get(transaction_hash, {})
    
    def get_nodes_info(self):
        """Get information about all nodes"""
        return self.nodes
    
    def get_quorum_slices(self):
        """Get quorum slice configuration"""
        return self.quorum_slices

# Global consensus instance
consensus = FBAConsensus()
