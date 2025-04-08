#!/usr/bin/env python3
import json
import base64
import argparse

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def encode_json_to_base64(s, t, p):
    """
    Create a JSON object with the given parameters and encode it with base64url.
    Base64URL is a URL-safe variant that replaces '+' with '-' and '/' with '_'.
    
    Args:
        s (str): The 's' parameter
        t (str): The 't' parameter
        p (str): The 'p' parameter
        
    Returns:
        str: Base64URL encoded JSON string
    """
    # Create the JSON object
    json_data = {"s":s,"t":t,"p":p}
    
    # Convert to JSON string
    json_string = json.dumps(json_data)
    # Remove any whitespace from the JSON string
    json_string = json_string.replace(" ", "")
    # Encode with base64url
    encoded = base64url_encode(json_string.encode('utf-8'))

    return encoded

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Encode JSON with base64url')
    parser.add_argument('--s', required=True, help='Value for the "s" parameter')
    parser.add_argument('--t', required=True, help='Value for the "t" parameter')
    parser.add_argument('--p', required=True, help='Value for the "p" parameter')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Encode JSON with base64url
    encoded = encode_json_to_base64(args.s, args.t, args.p)
    
    # Also print the decoded result to verify
    decoded = base64url_decode(encoded)
    print(f"{decoded}")
    print(f"{encoded}")


if __name__ == "__main__":
    main()
