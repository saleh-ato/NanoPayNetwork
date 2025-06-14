import hashlib
import base58

class AddressManager:
    """Manages FBA address generation and validation"""
    
    PREFIX = "fba_"
    
    @staticmethod
    def public_key_to_address(public_key_hex):
        """Convert public key to FBA address with checksum"""
        # Hash the public key
        pub_key_bytes = bytes.fromhex(public_key_hex)
        hash1 = hashlib.blake2b(pub_key_bytes, digest_size=32).digest()
        hash2 = hashlib.blake2b(hash1, digest_size=20).digest()
        
        # Add checksum
        checksum = hashlib.blake2b(hash2, digest_size=4).digest()
        address_bytes = hash2 + checksum
        
        # Encode with base58
        address_b58 = base58.b58encode(address_bytes).decode('utf-8')
        
        return f"{AddressManager.PREFIX}{address_b58}"
    
    @staticmethod
    def is_valid_address(address):
        """Validate FBA address format and checksum"""
        if not address.startswith(AddressManager.PREFIX):
            return False
        
        try:
            # Remove prefix and decode
            address_part = address[len(AddressManager.PREFIX):]
            address_bytes = base58.b58decode(address_part)
            
            if len(address_bytes) != 24:  # 20 + 4 checksum
                return False
            
            # Verify checksum
            payload = address_bytes[:-4]
            checksum = address_bytes[-4:]
            expected_checksum = hashlib.blake2b(payload, digest_size=4).digest()
            
            return checksum == expected_checksum
        except Exception:
            return False
    
    @staticmethod
    def get_address_info(address):
        """Get information about an address"""
        if not AddressManager.is_valid_address(address):
            return None
        
        return {
            'address': address,
            'prefix': AddressManager.PREFIX,
            'valid': True,
            'type': 'FBA Address'
        }
