import requests
import pandas as pd
import yaml
import urllib.parse
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BridgeAPIClient:
    
    def __init__(self, access_token: str, server_name: str = "test"):
        #Initialize Bridge API client
        self.access_token = access_token
        self.server_name = server_name
        self.base_url = "https://api.bridgedataoutput.com/api/v2"
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        #Make authenticated request to the Bridge API
        url = f"{self.base_url}/{endpoint}"
        
        # Add access token to params
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            logger.error(f"URL: {url}")
            if 'response' in locals():
                logger.error(f"Response: {response.text}")
            raise
    
    def get_listings(self, limit: int = 200, offset: int = 0) -> Dict[str, Any]:
        #Retrieve property listings from Bridge API
        params = {
            "limit": min(limit, 200),  # API enforces max of 200
            "offset": offset
        }
        
        endpoint = f"{self.server_name}/listings"
        return self._make_request(endpoint, params)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    #Load configuration from YAML file
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        logger.error(f"Config file {config_path} not found")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        raise

def search_properties_by_zip_codes(client: BridgeAPIClient, zip_codes: List[str], search_params: Dict[str, Any]) -> pd.DataFrame:                          
    #Search for properties and apply filters from config
    from utils import filter_properties
    
    all_listings = []
    
    logger.info(f"Fetching properties from Bridge API")
    logger.info(f"Filters from config: zips={zip_codes}, price={search_params.get('min_price')}-{search_params.get('max_price')}, beds>={search_params.get('min_beds')}, type={search_params.get('propertyType')}")
    
    try:
        response = client.get_listings(limit=200)
        
        if not response.get("success"):
            logger.warning(f"API returned success=false")
            return pd.DataFrame(all_listings)
            
        properties = response.get("bundle", [])
        logger.info(f"Retrieved {len(properties)} properties from API")
        
        for prop in properties:
                address = prop.get("UnparsedAddress", "")
                
                if not address:
                    street_number = prop.get("StreetNumber", "")
                    street_name = prop.get("StreetName", "")
                    street_suffix = prop.get("StreetSuffix", "")
                    unit = prop.get("UnitNumber", "")
                    
                    address_parts = [street_number, street_name, street_suffix]
                    address = " ".join([p for p in address_parts if p]).strip()
                    if unit:
                        address = f"{address} {unit}"
                
                if not address:
                    address = f"Listing {prop.get('ListingKey', 'Unknown')}"
                
                city = prop.get("City", "")
                state = prop.get("StateOrProvince", "")
                postal_code = prop.get("PostalCode", "")
                
                property_url = prop.get("url", "")
                
                price = prop.get("ListPrice") or prop.get("OriginalListPrice", 0)
                
                beds = prop.get("BedroomsTotal", 0)
                baths_full = prop.get("BathroomsFull", 0)
                baths_half = prop.get("BathroomsHalf", 0)
                total_baths = baths_full + (baths_half * 0.5)
                
                sqft = prop.get("LivingArea") or prop.get("AboveGradeFinishedArea", 0)
                
                listing = {
                    "zpid": prop.get("ListingKey", ""),
                    "address": address,
                    "city": city,
                    "state": state,
                    "postal_code": postal_code,
                    "price": price,
                    "beds": beds,
                    "baths": total_baths,
                    "sqft": sqft,
                    "propertySubType": prop.get("PropertySubType", "N/A"),
                    "property_url": property_url,
                    "status": prop.get("StandardStatus", "")
                }
                all_listings.append(listing)
            
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
    
    logger.info(f"Processed {len(all_listings)} total listings")
    df = pd.DataFrame(all_listings)
    
    if not df.empty:
        df = filter_properties(
            df,
            min_price=search_params.get("min_price"),
            max_price=search_params.get("max_price"),
            min_beds=search_params.get("min_beds"),
            min_baths=search_params.get("min_baths"),
            propertyType=search_params.get("propertyType")
        )
        logger.info(f"After applying config filters: {len(df)} properties")
    
    return df

def save_to_markdown(df: pd.DataFrame, config: Dict[str, Any]) -> str:
   #Save property data to a formatted markdown file
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"properties_report_{timestamp}.md"
    filepath = os.path.join("data", filename)
    
    markdown_content = []
    
    markdown_content.append("# Real Estate Property Report")
    markdown_content.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append("")
    
    markdown_content.append("## Search Criteria")
    markdown_content.append(f"- **Zip Codes:** {', '.join(config.get('zip_codes', []))}")
    markdown_content.append(f"- **Price Range:** ${config.get('min_price', 'N/A'):,} - ${config.get('max_price', 'N/A'):,}")
    markdown_content.append(f"- **Minimum Beds:** {config.get('min_beds', 'N/A')}")
    markdown_content.append(f"- **Minimum Baths:** {config.get('min_baths', 'N/A')}")
    markdown_content.append(f"- **Property Type:** {config.get('propertyType', 'N/A')}")
    markdown_content.append(f"- **Sort By:** {config.get('sort_by', 'N/A')}")
    markdown_content.append("")
    
    if not df.empty:
        markdown_content.append("## Summary Statistics")
        markdown_content.append(f"- **Total Properties Found:** {len(df)}")
        
        if 'price' in df.columns:
            avg_price = df['price'].mean()
            min_price = df['price'].min()
            max_price = df['price'].max()
            markdown_content.append(f"- **Average Price:** ${avg_price:,.2f}")
            markdown_content.append(f"- **Price Range:** ${min_price:,.0f} - ${max_price:,.0f}")
        
        if 'beds' in df.columns:
            avg_beds = df['beds'].mean()
            markdown_content.append(f"- **Average Bedrooms:** {avg_beds:.1f}")
        
        if 'baths' in df.columns:
            avg_baths = df['baths'].mean()
            markdown_content.append(f"- **Average Bathrooms:** {avg_baths:.1f}")
        
        if 'sqft' in df.columns:
            avg_sqft = df['sqft'].mean()
            markdown_content.append(f"- **Average Square Feet:** {avg_sqft:,.0f}")
        
        markdown_content.append("")
    
    if not df.empty:
        markdown_content.append("## Property Listings")
        markdown_content.append("")
        
        for idx, row in df.iterrows():
            address = row.get('address', 'N/A')
            city = row.get('city', 'N/A')
            state = row.get('state', 'N/A')
            price = row.get('price', 0)
            
            markdown_content.append(f"### {idx + 1}. {address}, {city}, {state}")
            
            if price > 0:
                markdown_content.append(f"**Price:** ${price:,}")
            
            beds = row.get('beds', 0)
            baths = row.get('baths', 0)
            if beds > 0 or baths > 0:
                markdown_content.append(f"**Bedrooms/Bathrooms:** {beds}/{baths}")
            
            sqft = row.get('sqft', 0)
            if sqft > 0:
                markdown_content.append(f"**Square Feet:** {sqft:,}")
        
            property_url = row.get('property_url', '')
            if property_url:
                markdown_content.append(f"**Zillow Link:** [{property_url}]({property_url})")
            
            markdown_content.append("")
    else:
        markdown_content.append("## No Properties Found")
        markdown_content.append("No properties were found matching your search criteria.")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_content))
    
    return filepath

def main():
    try:
        config = load_config()
        logger.info(f"Loaded configuration: {config}")
        
        client = BridgeAPIClient(
            access_token=config["access_token"],
            server_name=config.get("server_name", "test")
        )
        logger.info(f"Initialized Bridge API client (server: {config.get('server_name', 'test')})")
        
        search_params = {
            "min_price": config.get("min_price"),
            "max_price": config.get("max_price"),
            "min_beds": config.get("min_beds"),
            "min_baths": config.get("min_baths"),
            "propertyType": config.get("propertyType"),
            "sort_by": config.get("sort_by")
        }
        logger.info(f"Search parameters: {search_params}")
        
        df = search_properties_by_zip_codes(
            client=client,
            zip_codes=config["zip_codes"],
            search_params=search_params
        )
        
        if not df.empty:
            from utils import clean_property_data
            df = clean_property_data(df)
            logger.info(f"Found {len(df)} properties after cleaning")
            print("\n=== PROPERTY SEARCH RESULTS ===")
            
            display_columns = ['address', 'price', 'beds', 'baths', 'sqft', 'propertySubType', 'property_url']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                print(df[available_columns].head(10))
            else:
                print(df.head())
            
            import os
            os.makedirs("data", exist_ok=True)
            df.to_csv("data/properties.csv", index=False)
            logger.info("Properties saved to data/properties.csv")
            
            markdown_file = save_to_markdown(df, config)
            logger.info(f"Markdown report saved to {markdown_file}")
            
            print(f"\n=== SUMMARY ===")
            print(f"Total properties found: {len(df)}")
            if 'price' in df.columns:
                print(f"Average price: ${df['price'].mean():,.2f}")
                print(f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
            
            if 'property_url' in df.columns:
                print(f"\n=== SAMPLE PROPERTY URLs ===")
                sample_urls = df['property_url'].head(3).tolist()
                for i, url in enumerate(sample_urls, 1):
                    if url:
                        print(f"{i}. {url}")
        else:
            logger.info("No properties found matching criteria")
            print("No properties found matching your search criteria.")
            
    except FileNotFoundError:
        logger.error("Config file not found. Please ensure config.yaml exists.")
        print("Error: config.yaml file not found!")
    except KeyError as e:
        logger.error(f"Missing required configuration key: {e}")
        print(f"Error: Missing configuration key - {e}")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()