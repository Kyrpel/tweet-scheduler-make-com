import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import shutil

class CredentialsManager:
    def __init__(self):
        self.config_dir = Path.home() / '.tweet_scheduler'
        self.config_file = self.config_dir / 'config.json'
        self.credentials_dir = self.config_dir / 'credentials'
        self._setup_directories()
        self._setup_encryption()

    def _setup_directories(self):
        """Create necessary directories if they don't exist."""
        self.config_dir.mkdir(exist_ok=True)
        self.credentials_dir.mkdir(exist_ok=True)

    def _setup_encryption(self):
        """Setup encryption key."""
        key_file = self.config_dir / 'key.bin'
        if not key_file.exists():
            # Generate a new key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'tweet_scheduler_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b'tweet_scheduler_static_key'))
            key_file.write_bytes(key)
        
        self.fernet = Fernet(key_file.read_bytes())

    def save_credentials(self, openai_key: str, sheets_id: str, credentials_file) -> bool:
        """Save credentials to config file."""
        try:
            # Save Google credentials file
            creds_filename = 'google_credentials.json'
            creds_path = self.credentials_dir / creds_filename
            shutil.copy2(credentials_file, creds_path)

            # Encrypt sensitive data
            encrypted_openai_key = self.fernet.encrypt(openai_key.encode()).decode()
            encrypted_sheets_id = self.fernet.encrypt(sheets_id.encode()).decode()

            config = {
                'openai_key': encrypted_openai_key,
                'sheets_id': encrypted_sheets_id,
                'credentials_file': str(creds_path)
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f)

            return True
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False

    def load_credentials(self) -> dict:
        """Load credentials from config file."""
        try:
            if not self.config_file.exists():
                return None

            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Decrypt sensitive data
            openai_key = self.fernet.decrypt(config['openai_key'].encode()).decode()
            sheets_id = self.fernet.decrypt(config['sheets_id'].encode()).decode()

            return {
                'openai_key': openai_key,
                'sheets_id': sheets_id,
                'credentials_file': config['credentials_file']
            }
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

    def clear_credentials(self) -> bool:
        """Clear saved credentials."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            
            # Clear credentials directory
            for file in self.credentials_dir.glob('*'):
                file.unlink()
                
            return True
        except Exception as e:
            print(f"Error clearing credentials: {e}")
            return False
