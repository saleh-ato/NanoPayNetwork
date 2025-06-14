from flask import Blueprint, request, jsonify
from ledger.blockchain import ledger
from ledger.consensus import consensus
import logging

ledger_bp = Blueprint('ledger', __name__)

@ledger_bp.route('/stats', methods=['GET'])
def get_ledger_stats():
    """Get ledger statistics"""
    try:
        stats = ledger.get_ledger_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logging.error(f"Error getting ledger stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    """Get all confirmed transactions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        transactions = ledger.get_all_transactions()
        
        # Sort by timestamp (newest first) and limit
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        transactions = transactions[:limit]
        
        # Convert to dict format
        tx_data = [tx.to_dict() for tx in transactions]
        
        return jsonify({
            'success': True,
            'data': {
                'transactions': tx_data,
                'total': len(ledger.get_all_transactions())
            }
        })
    except Exception as e:
        logging.error(f"Error getting transactions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route('/pending', methods=['GET'])
def get_pending_transactions():
    """Get all pending transactions"""
    try:
        pending = ledger.get_pending_transactions()
        
        # Convert to dict format and add consensus info
        tx_data = []
        for tx in pending:
            tx_dict = tx.to_dict()
            consensus_status = consensus.get_consensus_status(tx.hash)
            tx_dict['consensus'] = consensus_status
            tx_data.append(tx_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'transactions': tx_data,
                'count': len(pending)
            }
        })
    except Exception as e:
        logging.error(f"Error getting pending transactions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route('/consensus/<transaction_hash>', methods=['GET'])
def get_consensus_status(transaction_hash):
    """Get consensus status for a specific transaction"""
    try:
        consensus_status = consensus.get_consensus_status(transaction_hash)
        node_votes = consensus.get_node_votes(transaction_hash)
        
        return jsonify({
            'success': True,
            'data': {
                'transaction_hash': transaction_hash,
                'consensus': consensus_status,
                'votes': node_votes
            }
        })
    except Exception as e:
        logging.error(f"Error getting consensus status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route('/nodes', methods=['GET'])
def get_nodes():
    """Get information about all FBA nodes"""
    try:
        nodes = consensus.get_nodes_info()
        quorum_slices = consensus.get_quorum_slices()
        
        return jsonify({
            'success': True,
            'data': {
                'nodes': nodes,
                'quorum_slices': quorum_slices
            }
        })
    except Exception as e:
        logging.error(f"Error getting nodes info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ledger_bp.route('/faucet', methods=['POST'])
def faucet():
    """Faucet to get test coins (educational purposes)"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'error': 'Address required'}), 400
        
        # Create faucet transaction
        from wallet.transaction import Transaction
        
        tx = Transaction(
            from_address='genesis',
            to_address=address,
            amount=100.0  # Give 100 FBA coins
        )
        
        # Simple hash for genesis transactions
        tx.hash = tx.calculate_hash()
        tx.signature = 'genesis_signature'
        
        # Add transaction directly (bypass normal validation for faucet)
        ledger.add_transaction(tx)
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Faucet successful! 100 FBA coins sent.',
                'transaction_hash': tx.hash,
                'amount': 100.0
            }
        })
    except Exception as e:
        logging.error(f"Error in faucet: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
