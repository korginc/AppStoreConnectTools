import requests
import json
import argparse

def fetch_apps(token):
    """
    Fetch app names and IDs from App Store Connect API
    
    Args:
        token (str): App Store Connect API token
        
    Returns:
        list: List of dictionaries containing app information
    """
    endpoint = "https://api.appstoreconnect.apple.com/v1/apps?fields[apps]=name,bundleId"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        apps = []
        
        if 'data' in data:
            for app in data['data']:
                app_info = {
                    'id': app['id'],
                    'name': app['attributes']['name'] if 'attributes' in app and 'name' in app['attributes'] else 'Unknown',
                    'bundleId': app['attributes']['bundleId'] if 'attributes' in app and 'bundleId' in app['attributes'] else 'Unknown'
                }
                apps.append(app_info)
        
        return apps
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching apps: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []

def fetch_in_app_purchases(token, app_id):
    """
    Fetch in-app purchases for a specific app from App Store Connect API
    
    Args:
        token (str): App Store Connect API token
        app_id (str): App ID to fetch in-app purchases for
        
    Returns:
        list: List of dictionaries containing in-app purchase information
    """
    endpoint = f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/inAppPurchasesV2?limit=200"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        iaps = []
        
        if 'data' in data:
            for iap in data['data']:
                iap_info = {
                    'id': iap['id'],
                    'name': iap['attributes']['name'] if 'attributes' in iap and 'name' in iap['attributes'] else 'Unknown',
                    'productId': iap['attributes']['productId'] if 'attributes' in iap and 'productId' in iap['attributes'] else 'Unknown'
                }
                iaps.append(iap_info)
        
        return iaps
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching in-app purchases for app {app_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Fetch apps and in-app purchases from App Store Connect')
    parser.add_argument('--token', required=True, help='App Store Connect API token')
    args = parser.parse_args()
    
    apps = fetch_apps(args.token)
    
    if apps:
        for app in apps:
            print(f"{app['name']},{app['bundleId']},{app['id']}")
        
        for app in apps:
            iaps = fetch_in_app_purchases(args.token, app['id'])
            if iaps:
                for iap in iaps:
                    print(f"{iap['name']},{iap['productId']},{iap['id']},{app['name']}")
    else:
        print("No apps found or error occurred.")

if __name__ == "__main__":
    main()
