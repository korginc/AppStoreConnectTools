#!/usr/bin/env python3
import json
import requests
import subprocess
import argparse
import sys
import csv
from datetime import datetime
from collections import defaultdict

def get_item_type_definitions(item_type: str) -> dict:
    """
    Get the type definitions for a specific item type (apps or inAppPurchases).
    
    Args:
        item_type (str): Either 'apps' or 'inAppPurchases'
        
    Returns:
        dict: Dictionary containing all type definitions for the item type
        
    Raises:
        ValueError: If item_type is not 'apps' or 'inAppPurchases'
    """
    ITEM_TYPES = {
        "apps": {
            "product_type":  "app",
            "products_type": "apps",
            "prices_type": "appPrices",
            "price_point_type":  "appPricePoint",
            "price_points_type": "appPricePoints",
            "schedule_type": "appPriceSchedules",
            "endpoint": "https://api.appstoreconnect.apple.com/v1/appPriceSchedules"
        },
        "inAppPurchases": {
            "product_type":  "inAppPurchase",
            "products_type": "inAppPurchases",
            "prices_type": "inAppPurchasePrices",
            "price_point_type":  "inAppPurchasePricePoint",
            "price_points_type": "inAppPurchasePricePoints",
            "schedule_type": "inAppPurchasePriceSchedules",
            "endpoint": "https://api.appstoreconnect.apple.com/v1/inAppPurchasePriceSchedules"
        }
    }
    
    if item_type not in ITEM_TYPES:
        raise ValueError(f"Invalid item_type: {item_type}. Must be 'apps' or 'inAppPurchases'")
    
    return ITEM_TYPES[item_type]

def get_price_point_id(app_id, territory, price_point):
    """
    Get the price point ID using the createPricePointID.py script
    
    Args:
        app_id (str): The app ID
        territory (str): The territory code (e.g., USA, JPN)
        price_point (str): The price point code
        
    Returns:
        str: The base64 encoded price point ID
    """
    try:
        result = subprocess.run(
            ['python3', 'createPricePointID.py', '--s', app_id, '--t', territory, '--p', price_point],
            capture_output=True,
            text=True,
            check=True
        )
        # The script prints the encoded ID on the last line
        return result.stdout.strip().split('\n')[-1]
    except subprocess.CalledProcessError as e:
        print(f"Error getting price point ID: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def prepare_price_data(price: dict, index: int, types: dict, app_id: str) -> tuple:
    """
    Prepare price data objects for the API request.
    
    Args:
        price (dict): Price information including territory and price point
        index (int): Index of the price in the sequence
        types (dict): Type definitions for the item type
        app_id (str): The app or IAP ID
        
    Returns:
        tuple: A tuple containing (manual_price_data, included_price_data)
    """
    territory = price.get('territory')
    price_point = price.get('price')
    
    # Get the price point ID
    price_point_id = get_price_point_id(app_id, territory, price_point)
    
    # Create a unique ID for this price
    price_id = "${price-" + str(index) + "}"
    
    # Create manual price data
    manual_price_data = {
        "type": types["prices_type"],
        "id": price_id
    }
    
    # Create included price data
    included_price_data = {
        "id": price_id,
        "type": types["prices_type"],
        "relationships": {
            types["price_point_type"]: {
                "data": {
                    "type": types["price_points_type"],
                    "id": price_point_id
                }
            }
        }
    }
    
    # Add start and end dates if provided
    attributes = {}
    if price.get('startDate'):
        attributes['startDate'] = price.get('startDate')
    if price.get('endDate'):
        attributes['endDate'] = price.get('endDate')
    
    if attributes:
        included_price_data['attributes'] = attributes
        
    return manual_price_data, included_price_data

def update_price_schedule(token, app_id, item_type, prices, dry_run=False):
    """
    Update the price schedule for an app or IAP
    
    Args:
        token (str): The App Store Connect API token
        app_id (str): The app or IAP ID
        item_type (str): Either 'apps' or 'inAppPurchases'
        prices (list): List of price objects with territory, price, startDate, and endDate
        dry_run (bool): If True, only print the payload without making the API request
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ValueError: If item_type is not 'apps' or 'inAppPurchases'
    """
    # Get type definitions for the item type
    types = get_item_type_definitions(item_type)
    
    # Prepare the manual prices data
    manual_prices_data = []
    included_data = []
    
    for i, price in enumerate(prices):
        manual_price_data, included_price_data = prepare_price_data(price, i, types, app_id)
        manual_prices_data.append(manual_price_data)
        included_data.append(included_price_data)
    
    # Prepare the JSON payload
    payload = {
        "data": {
            "type": types["schedule_type"],
            "relationships": {
                types["product_type"]: {
                    "data": {
                        "type": types["products_type"],
                        "id": app_id
                    }
                },
                "baseTerritory": {
                    "data": {
                        "type": "territories",
                        "id": prices[0].get('territory')  # Use the first territory as base
                    }
                },
                "manualPrices": {
                    "data": manual_prices_data
                }
            }
        },
        "included": included_data
    }
    
    if dry_run:
        print(f"Dry run: Payload for {item_type} {app_id}:")
        print(json.dumps(payload, indent=2))
        return True
    
    # Make the API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(types["endpoint"], headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully updated price schedule for {item_type} {app_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating price schedule: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update App Store Connect price schedules')
    parser.add_argument('--token', required=True, help='App Store Connect API token')
    parser.add_argument('--csv', default='app-price-schedule.csv', help='Path to the CSV file with price schedule data')
    parser.add_argument('--dry-run', action='store_true', help='Print the payload without making the API request')
    args = parser.parse_args()
    
    # Read the CSV file and group items by ID
    try:
        with open(args.csv, 'r') as f:
            reader = csv.DictReader(f)
            
            # Check for required columns
            required_columns = ['input', 'id', 'type', 'territory', 'price', 'start', 'end', 'price_point_id']
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                print(f"Error: CSV file is missing required columns: {', '.join(missing_columns)}")
                sys.exit(1)
            
            # Group items by ID
            grouped_items = defaultdict(lambda: {"memo": "", "id": "", "type": "", "prices": []})
            
            for row in reader:
                # Skip if memo is empty
                if not row['input'].strip():
                    continue
                    
                item_id = row['id']
                if not item_id:
                    continue
                    
                # Add or update the group
                if not grouped_items[item_id]["id"]:
                    grouped_items[item_id]["memo"] = row['input']
                    grouped_items[item_id]["id"] = item_id
                    grouped_items[item_id]["type"] = row['type']
                
                # Add price to the group
                price = {
                    'territory': row['territory'],
                    'price': row['price_point_id'],
                    'startDate': None if row['start'] == "null" else row['start'],
                    'endDate': None if row['end'] == "null" else row['end']
                }
                grouped_items[item_id]["prices"].append(price)
            
            # Convert to list for processing
            items = list(grouped_items.values())
            
    except FileNotFoundError:
        print(f"Error: {args.csv} file not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Process each item
    for item in items:
        app_id = item.get('id')
        item_type = item.get('type')
        memo = item.get('memo', 'Unknown')
        prices = item.get('prices', [])
        
        if not app_id or not item_type or not prices:
            print(f"Skipping item {memo}: Missing required fields")
            continue
        
        print(f"Processing {item_type} {app_id} ({memo}) with {len(prices)} prices")
        try:
            success = update_price_schedule(args.token, app_id, item_type, prices, args.dry_run)
            if not success:
                print(f"Failed to update price schedule for {item_type} {app_id}")
        except ValueError as e:
            print(f"Error processing {memo}: {e}")
            continue

if __name__ == "__main__":
    main()
