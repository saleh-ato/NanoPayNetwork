import os
import logging
from flask import Flask, render_template, jsonify, request
from api.wallet_api import wallet_bp
from api.ledger_api import ledger_bp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-demo")

# Register blueprints
app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
app.register_blueprint(ledger_bp, url_prefix='/api/ledger')

@app.route('/')
def index():
    """Serve the main wallet interface"""
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
