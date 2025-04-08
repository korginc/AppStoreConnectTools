#!/usr/bin/env python3
import base64
import jwt
import json
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants from environment variables
ISSUER_ID = os.getenv('APPSTORE_ISSUER_ID')
KEY_ID = os.getenv('APPSTORE_KEY_ID')
PRIVATE_KEY_PATH = os.getenv('APPSTORE_PRIVATE_KEY_PATH')

def create_token():
    """Create a JWT token for App Store Connect API authentication."""
    if not all([ISSUER_ID, KEY_ID, PRIVATE_KEY_PATH]):
        raise ValueError("Missing required environment variables. Please check your .env file.")
    
    try:
        with open(PRIVATE_KEY_PATH, 'r') as key_file:
            private_key = key_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found at {PRIVATE_KEY_PATH}")
    
    payload = {
        'iss': ISSUER_ID,
        'exp': int((datetime.now() + timedelta(minutes=20)).timestamp()),
        'aud': 'appstoreconnect-v1'
    }
    
    headers = {
        'kid': KEY_ID,
        'typ': 'JWT'
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers=headers
    )
    
    return token

if __name__ == "__main__":
    token = create_token()
    print(token) 