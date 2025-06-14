import os
import hashlib
import secrets
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
import json

class KeyManager:
    """Manages ed25519 key generation and operations"""
    
    @staticmethod
    def generate_keypair():
        """Generate a new ed25519 keypair"""
        private_key = SigningKey.generate()
        public_key = private_key.verify_key
        
        return {
            'private_key': private_key.encode(encoder=HexEncoder).decode('utf-8'),
            'public_key': public_key.encode(encoder=HexEncoder).decode('utf-8')
        }
    
    @staticmethod
    def generate_seed():
        """Generate a 32-byte seed for key derivation"""
        return secrets.token_hex(32)
    
    @staticmethod
    def keypair_from_seed(seed_hex):
        """Derive keypair from seed"""
        seed_bytes = bytes.fromhex(seed_hex)
        private_key = SigningKey(seed_bytes)
        public_key = private_key.verify_key
        
        return {
            'private_key': private_key.encode(encoder=HexEncoder).decode('utf-8'),
            'public_key': public_key.encode(encoder=HexEncoder).decode('utf-8')
        }
    
    @staticmethod
    def sign_message(private_key_hex, message):
        """Sign a message with private key"""
        private_key = SigningKey(private_key_hex, encoder=HexEncoder)
        message_bytes = message.encode('utf-8') if isinstance(message, str) else message
        signature = private_key.sign(message_bytes)
        return signature.signature.hex()
    
    @staticmethod
    def verify_signature(public_key_hex, message, signature_hex):
        """Verify a signature"""
        try:
            public_key = VerifyKey(public_key_hex, encoder=HexEncoder)
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(message_bytes, signature_bytes)
            return True
        except Exception:
            return False
