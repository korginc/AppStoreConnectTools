#!/usr/bin/env python3
import json
import requests
import subprocess
import argparse
import sys
import csv
from datetime import datetime
from collections import defaultdict

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

def update_price_schedule(token, app_id, item_type, prices, debug=False):
    """
    Update the price schedule for an app or IAP
    
    Args:
        token (str): The App Store Connect API token
        app_id (str): The app or IAP ID
        item_type (str): Either 'apps' or 'inAppPurchases'
        prices (list): List of price objects with territory, price, startDate, and endDate
        debug (bool): Whether to print debug information
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ValueError: If item_type is not 'apps' or 'inAppPurchases'
    """
    # Validate item_type
    if item_type not in ["apps", "inAppPurchases"]:
        raise ValueError(f"Invalid item_type: {item_type}. Must be 'apps' or 'inAppPurchases'")
    
    # Determine the price types based on item type
    if item_type == "apps":
        product_type = "app"
        prices_type = "appPrices"
        price_point_type = "appPricePoint"
        price_points_type = "appPricePoints"
    else:  # inAppPurchases
        product_type = "inAppPurchase"
        prices_type = "inAppPurchasePrices"
        price_point_type = "inAppPurchasePricePoint"
        price_points_type = "inAppPurchasePricePoints"
    
    # Prepare the manual prices data
    manual_prices_data = []
    included_data = []
    
    for i, price in enumerate(prices):
        territory = price.get('territory')
        price_point = price.get('price')
        
        # Get the price point ID
        price_point_id = get_price_point_id(app_id, territory, price_point)
        
        # Create a unique ID for this price
        price_id = "${price-" + str(i) + "}"
        
        # Add to manual prices data
        manual_prices_data.append({
            "type": prices_type,
            "id": price_id
        })
        
        # Add to included data
        price_data = {
            "id": price_id,
            "type": prices_type,
            "relationships": {
                price_point_type: {
                    "data": {
                        "type": price_points_type,
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
            price_data['attributes'] = attributes
            
        included_data.append(price_data)
    
    # Determine the schedule type based on item type
    if item_type == "apps":
        schedule_type = "appPriceSchedules"
    else:  # inAppPurchases
        schedule_type = "inAppPurchasePriceSchedules"
    
    # Prepare the JSON payload
    payload = {
        "data": {
            "type": schedule_type,
            "relationships": {
                product_type: {
                    "data": {
                        "type": item_type,
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
    
    if debug:
        print(f"Debug: Payload for {item_type} {app_id}:")
        print(json.dumps(payload, indent=2))
    
    # Determine the API endpoint based on item type
    if item_type == "apps":
        endpoint = f"https://api.appstoreconnect.apple.com/v1/appPriceSchedules"
    else:  # inAppPurchases
        endpoint = f"https://api.appstoreconnect.apple.com/v1/inAppPurchasePriceSchedules"
    
    # Make the API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
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
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to print payload')
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
            success = update_price_schedule(args.token, app_id, item_type, prices, args.debug)
            if not success:
                print(f"Failed to update price schedule for {item_type} {app_id}")
        except ValueError as e:
            print(f"Error processing {memo}: {e}")
            continue

if __name__ == "__main__":
    main()
