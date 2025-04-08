#!/usr/bin/env python3
import json
import base64
import argparse

def encode_json_to_base64(s, t, p):
    """
    Create a JSON object with the given parameters and encode it with base64.
    
    Args:
        s (str): The 's' parameter
        t (str): The 't' parameter
        p (str): The 'p' parameter
        
    Returns:
        str: Base64 encoded JSON string
    """
    # Create the JSON object
    json_data = {"s":s,"t":t,"p":p}
    
    # Convert to JSON string
    json_string = json.dumps(json_data)
    # Remove any whitespace from the JSON string
    json_string = json_string.replace(" ", "")
    # Encode with base64
    encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

    return encoded

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Encode JSON with base64')
    parser.add_argument('--s', required=True, help='Value for the "s" parameter')
    parser.add_argument('--t', required=True, help='Value for the "t" parameter')
    parser.add_argument('--p', required=True, help='Value for the "p" parameter')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Encode JSON with base64
    encoded = encode_json_to_base64(args.s, args.t, args.p)
    
    # Also print the decoded result to verify
    decoded = base64.b64decode(encoded).decode('utf-8')
    print(f"{decoded}")

    # Remove any padding characters (=) from the end of the encoded string
    final_string = encoded.rstrip('=')
    print(f"{final_string}")


if __name__ == "__main__":
    main()
