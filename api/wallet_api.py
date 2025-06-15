from flask import Blueprint, request, jsonify
from wallet.keys import KeyManager
from wallet.address import AddressManager
from wallet.transaction import Transaction
from ledger.blockchain import ledger
from ledger.consensus import consensus
import logging

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/generate', methods=['POST'])
def generate_wallet():
    """Generate a new wallet keypair and address"""
    try:
        # Generate seed first
        seed = KeyManager.generate_seed()
        
        # Generate keypair from seed
        keypair = KeyManager.keypair_from_seed(seed)
        
        # Generate address from public key
        address = AddressManager.public_key_to_address(keypair['public_key'])
        
        return jsonify({
            'success': True,
            'data': {
                'seed': seed,
                'private_key': keypair['private_key'],
                'public_key': keypair['public_key'],
                'address': address
            }
        })
    except Exception as e:
        logging.error(f"Error generating wallet: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@wallet_bp.route('/import', methods=['POST'])
def import_wallet():
    """Import wallet from seed or private key"""
    try:
        data = request.get_json()
        
        if 'seed' in data:
            # Import from seed
            keypair = KeyManager.keypair_from_seed(data['seed'])
        elif 'private_key' in data:
            # Import from private key
            keypair = {'private_key': data['private_key']}
            # Derive public key (simplified - in real implementation would derive from private key)
            return jsonify({'success': False, 'error': 'Private key import not fully implemented'}), 400
        else:
            return jsonify({'success': False, 'error': 'Seed or private key required'}), 400
        
        # Generate address
        address = AddressManager.public_key_to_address(keypair['public_key'])
        
        return jsonify({
            'success': True,
            'data': {
                'private_key': keypair['private_key'],
                'public_key': keypair['public_key'],
                'address': address
            }
        })
    except Exception as e:
        logging.error(f"Error importing wallet: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@wallet_bp.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    """Get balance for an address"""
    try:
        if not AddressManager.is_valid_address(address):
            return jsonify({'success': False, 'error': 'Invalid address format'}), 400
        
        balance = ledger.get_balance(address)
        
        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'balance': balance
            }
        })
    except Exception as e:
        logging.error(f"Error getting balance: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@wallet_bp.route('/history/<address>', methods=['GET'])
def get_transaction_history(address):
    """Get transaction history for an address"""
    try:
        if not AddressManager.is_valid_address(address):
            return jsonify({'success': False, 'error': 'Invalid address format'}), 400
        
        limit = request.args.get('limit', 10, type=int)
        transactions = ledger.get_transaction_history(address, limit)
        
        # Convert transactions to dict format
        tx_data = []
        for tx in transactions:
            tx_dict = tx.to_dict()
            # Add transaction type for display
            tx_dict['type'] = 'sent' if tx.from_address == address else 'received'
            tx_data.append(tx_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'transactions': tx_data
            }
        })
    except Exception as e:
        logging.error(f"Error getting transaction history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@wallet_bp.route('/send', methods=['POST'])
def send_transaction():
    """Create and broadcast a transaction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_address', 'to_address', 'amount', 'private_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Validate addresses
        if not AddressManager.is_valid_address(data['from_address']):
            return jsonify({'success': False, 'error': 'Invalid from_address'}), 400
        
        if not AddressManager.is_valid_address(data['to_address']):
            return jsonify({'success': False, 'error': 'Invalid to_address'}), 400
        
        # Create transaction
        tx = Transaction(
            from_address=data['from_address'],
            to_address=data['to_address'],
            amount=float(data['amount'])
        )
        
        # Sign transaction
        tx.sign_transaction(data['private_key'])
        
        # Add proof-of-work (simple demonstration)
        tx.mine_transaction(difficulty=2)
        
        # Add to pending transactions
        if ledger.add_pending_transaction(tx):
            # Simulate consensus voting
            consensus.simulate_vote(tx.hash)
            
            # Check if consensus is reached
            consensus_status = consensus.check_consensus(tx.hash)
            
            if consensus_status == 'consensus_accept':
                # Add to confirmed transactions
                ledger.add_transaction(tx)
                status = 'confirmed'
            else:
                status = 'pending'
            
            return jsonify({
                'success': True,
                'data': {
                    'transaction_hash': tx.hash,
                    'status': status,
                    'transaction': tx.to_dict()
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Transaction validation failed'}), 400
            
    except Exception as e:
        logging.error(f"Error sending transaction: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@wallet_bp.route('/validate/<address>', methods=['GET'])
def validate_address(address):
    """Validate an FBA address"""
    try:
        is_valid = AddressManager.is_valid_address(address)
        address_info = AddressManager.get_address_info(address) if is_valid else None
        
        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'valid': is_valid,
                'info': address_info
            }
        })
    except Exception as e:
        logging.error(f"Error validating address: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
