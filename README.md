# App Store Connect API Price Management Tool

This tool helps manage and update prices for your App Store Connect applications and in-app purchases using the App Store Connect API.

## Features

- JWT token authentication with App Store Connect API
- Fetch app information and details
- Retrieve IAP (In-App Purchase) prices
- Update prices for apps and IAPs
- Comprehensive error handling and logging

## Dependencies

The project uses the following main dependencies:

- `PyJWT==2.10.1`: For creating and handling JSON Web Tokens (JWT) for API authentication
- `requests==2.32.3`: For making HTTP requests to the App Store Connect API
- `cryptography==44.0.2`: Required for ES256 algorithm support in JWT token creation
- `python-dotenv==1.1.0`: For managing environment variables and sensitive credentials

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
4. Update the `.env` file with your App Store Connect API credentials:
   ```
   APPSTORE_ISSUER_ID="your-issuer-id"
   APPSTORE_KEY_ID="your-key-id"
   APPSTORE_PRIVATE_KEY_PATH="path/to/your/private/key.p8"
   ```

## Using updatePrice.py

The `updatePrice.py` script provides a command-line interface for updating prices in bulk. Here's how to use it:

### Basic Usage

```bash
python updatePrice.py --token YOUR_JWT_TOKEN --csv price-schedule.csv
```

### Command Line Arguments

- `--token`: App Store Connect API token (required)
- `--csv`: Path to the CSV file with price schedule data (default: 'app-price-schedule.csv')
- `--debug`: Enable debug mode to print payload (optional)

### CSV File Format

The input CSV file should contain the following columns:
- `input`: Memo or description of the item
- `id`: The app or IAP ID
- `type`: Either 'apps' or 'inAppPurchases'
- `territory`: Territory code (e.g., USA, JPN)
- `price`: Price point code
- `start`: Start date (use "null" for no start date)
- `end`: End date (use "null" for no end date)
- `price_point_id`: Price point identifier
Please take a look at `sample.csv` for the details.

## Creating Price Point IDs

The `createPricePointID.py` script is used to generate price point IDs required for the price schedule updates. This script encodes parameters into a base64 string that serves as a price point identifier.

### Basic Usage


Example CSV content:
```csv
input,id,type,territory,price,start,end,price_point_id
My App,1234567890,apps,USA,0.00,null,null,10000
My App,1234567890,apps,JPN,50,2024-03-01,null,10001
My IAP,9876543210,inAppPurchases,USA,9.99,null,null,10127
```

### How It Works

1. The script reads the CSV file and groups items by their ID
2. For each item:
   - Validates the required fields
   - Groups prices by territory
   - Creates price point IDs using the createPricePointID.py script
   - Updates the price schedule via the App Store Connect API

### Error Handling

The script handles various error cases:
- Missing required CSV columns
- Invalid item types
- API authentication errors
- Network issues
- Invalid price formats

All errors are logged to the console with detailed messages.

### Example Usage

1. Update prices using a CSV file:
   ```bash
   python updatePrice.py --token YOUR_JWT_TOKEN --csv my-prices.csv
   ```

2. Enable debug mode to see the API payload:
   ```bash
   python updatePrice.py --token YOUR_JWT_TOKEN --csv my-prices.csv --debug
   ```

### Related Scripts

This script works in conjunction with:
- `createPricePointID.py`: Generates price point IDs
- `getItemIds.py`: Fetches app and IAP IDs from App Store Connect

## Security

- All sensitive credentials are stored in the `.env` file
- The `.env` file is excluded from version control
- JWT tokens are automatically generated and expire after 20 minutes
- Private keys are stored securely and accessed via environment variables

## License

This project is licensed under the MIT License - see the LICENSE file for details. 