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

class ZillowRapidAPIClient:
    """Client for RapidAPI Zillow API endpoints"""
    
    def __init__(self, api_key: str, host: str = "zillow-com1.p.rapidapi.com"):
        self.api_key = api_key
        self.host = host
        self.base_url = f"https://{host}"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the RapidAPI Zillow endpoint"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def search_properties(self, 
                         location: str,
                         min_price: Optional[int] = None,
                         max_price: Optional[int] = None,
                         min_beds: Optional[int] = None,
                         max_beds: Optional[int] = None,
                         min_baths: Optional[int] = None,
                         property_type: Optional[str] = None,
                         sort_by: str = "newest",
                         limit: int = 20) -> Dict[str, Any]:
        """
        Search for properties using RapidAPI Zillow endpoint
        
        Args:
            location: City, state, or zip code to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_beds: Minimum bedrooms
            max_beds: Maximum bedrooms
            min_baths: Minimum bathrooms
            property_type: Type of property (house, condo, etc.)
            sort_by: Sort results by (newest, price_asc, price_desc)
            limit: Number of results to return
        """
        params = {
            "location": location,
            "limit": limit,
            "sort": sort_by
        }
        
        if min_price:
            params["minPrice"] = min_price
        if max_price:
            params["maxPrice"] = max_price
        if min_beds:
            params["bedsMin"] = min_beds
        if max_beds:
            params["bedsMax"] = max_beds
        if min_baths:
            params["bathsMin"] = min_baths
        if property_type:
            params["propertyType"] = property_type
        
        return self._make_request("propertyExtendedSearch", params)
    
    def get_property_details(self, zpid: str) -> Dict[str, Any]:
        """Get detailed information about a specific property by ZPID"""
        params = {"zpid": zpid}
        return self._make_request("property", params)
    
    
    def get_property_by_url(self, property_url: str) -> Dict[str, Any]:
        """Get property details by Zillow URL"""
        params = {"url": property_url}
        return self._make_request("propertyByUrl", params)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
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

def search_properties_by_zip_codes(client: ZillowRapidAPIClient, 
                                  zip_codes: List[str], 
                                  search_params: Dict[str, Any]) -> pd.DataFrame:
    """
    Search for properties across multiple zip codes and return as DataFrame
    
    Args:
        client: ZillowRapidAPIClient instance
        zip_codes: List of zip codes to search
        search_params: Search parameters from config
    """
    all_listings = []
    
    for zip_code in zip_codes:
        logger.info(f"Searching properties in zip code: {zip_code}")
        
        try:
            response = client.search_properties(
                location=zip_code,
                min_price=search_params.get("min_price"),
                max_price=search_params.get("max_price"),
                min_beds=search_params.get("min_beds"),
                min_baths=search_params.get("min_baths"),
                property_type=search_params.get("property_types", ["house"])[0] if search_params.get("property_types") else None,
                sort_by=search_params.get("sort_by", "newest")
            )
            
            # Process the response based on RapidAPI Zillow format
            properties = response.get("props", []) or response.get("data", []) or response.get("results", [])
            
            for prop in properties:
                # Build Zillow property URL if not provided
                property_url = prop.get("detailUrl", "")
                if not property_url and prop.get("zpid"):
                    # Construct Zillow URL from address and zpid if detailUrl is missing
                    address = prop.get("address", "").replace(" ", "-")
                    city = prop.get("city", "").replace(" ", "-")
                    state = prop.get("state", "")
                    zpid = prop.get("zpid")
                    if address and city and state and zpid:
                        property_url = f"https://www.zillow.com/homedetails/{address}-{city}-{state}/{zpid}_zpid"
                
                listing = {
                    "zpid": prop.get("zpid"),
                    "address": prop.get("address", ""),
                    "city": prop.get("city", ""),
                    "state": prop.get("state", ""),
                    "zipcode": prop.get("zipcode", zip_code),
                    "price": prop.get("price", 0),
                    "beds": prop.get("bedrooms", 0),
                    "baths": prop.get("bathrooms", 0),
                    "sqft": prop.get("livingArea", 0),
                    "property_type": prop.get("homeType", ""),
                    "listing_date": prop.get("datePosted", ""),
                    "property_url": property_url,
                    "days_on_zillow": prop.get("daysOnZillow", 0),
                    "price_per_sqft": prop.get("pricePerSquareFoot", 0)
                }
                all_listings.append(listing)
                
        except Exception as e:
            logger.error(f"Error searching zip code {zip_code}: {e}")
            continue
    
    return pd.DataFrame(all_listings)

def save_to_markdown(df: pd.DataFrame, config: Dict[str, Any]) -> str:
    """Save property data to a formatted markdown file"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"properties_report_{timestamp}.md"
    filepath = os.path.join("data", filename)
    
    # Start building markdown content
    markdown_content = []
    
    # Header
    markdown_content.append("# Real Estate Property Report")
    markdown_content.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append("")
    
    # Search criteria
    markdown_content.append("## Search Criteria")
    markdown_content.append(f"- **Zip Codes:** {', '.join(config.get('zip_codes', []))}")
    markdown_content.append(f"- **Price Range:** ${config.get('min_price', 'N/A'):,} - ${config.get('max_price', 'N/A'):,}")
    markdown_content.append(f"- **Minimum Beds:** {config.get('min_beds', 'N/A')}")
    markdown_content.append(f"- **Minimum Baths:** {config.get('min_baths', 'N/A')}")
    markdown_content.append(f"- **Property Types:** {', '.join(config.get('property_types', []))}")
    markdown_content.append(f"- **Sort By:** {config.get('sort_by', 'N/A')}")
    markdown_content.append("")
    
    # Summary statistics
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
    
    # Property listings
    if not df.empty:
        markdown_content.append("## Property Listings")
        markdown_content.append("")
        
        for idx, row in df.iterrows():
            # Property header
            address = row.get('address', 'N/A')
            city = row.get('city', 'N/A')
            state = row.get('state', 'N/A')
            price = row.get('price', 0)
            
            markdown_content.append(f"### {idx + 1}. {address}, {city}, {state}")
            
            # Property details
            if price > 0:
                markdown_content.append(f"**Price:** ${price:,}")
            
            beds = row.get('beds', 0)
            baths = row.get('baths', 0)
            if beds > 0 or baths > 0:
                markdown_content.append(f"**Bedrooms/Bathrooms:** {beds}/{baths}")
            
            sqft = row.get('sqft', 0)
            if sqft > 0:
                markdown_content.append(f"**Square Feet:** {sqft:,}")
            
            property_type = row.get('property_type', '')
            if property_type:
                markdown_content.append(f"**Property Type:** {property_type}")
            
            days_on_zillow = row.get('days_on_zillow', 0)
            if days_on_zillow > 0:
                markdown_content.append(f"**Days on Zillow:** {days_on_zillow}")
            
            price_per_sqft = row.get('price_per_sqft', 0)
            if price_per_sqft > 0:
                markdown_content.append(f"**Price per Sq Ft:** ${price_per_sqft:.2f}")
            
            # Zillow URL
            property_url = row.get('property_url', '')
            if property_url:
                markdown_content.append(f"**Zillow Link:** [{property_url}]({property_url})")
            
            markdown_content.append("")
    else:
        markdown_content.append("## No Properties Found")
        markdown_content.append("No properties were found matching your search criteria.")
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_content))
    
    return filepath

def main():
    """Main function to demonstrate the API usage"""
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration: {config}")
        
        # Initialize client
        client = ZillowRapidAPIClient(
            api_key=config["api_key"],
            host=config["host"]
        )
        logger.info(f"Initialized client for host: {config['host']}")
        
        # Search parameters from config
        search_params = {
            "min_price": config.get("min_price"),
            "max_price": config.get("max_price"),
            "min_beds": config.get("min_beds"),
            "min_baths": config.get("min_baths"),
            "property_types": config.get("property_types"),
            "sort_by": config.get("sort_by")
        }
        logger.info(f"Search parameters: {search_params}")
        
        # Search properties
        df = search_properties_by_zip_codes(
            client=client,
            zip_codes=config["zip_codes"],
            search_params=search_params
        )
        
        if not df.empty:
            # Clean data and remove duplicates
            from utils import clean_property_data
            df = clean_property_data(df)
            logger.info(f"Found {len(df)} properties")
            print("\n=== PROPERTY SEARCH RESULTS ===")
            
            # Display key columns with URLs
            display_columns = ['address', 'city', 'state', 'price', 'beds', 'baths', 'sqft', 'property_url']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                print(df[available_columns].head(10))
            else:
                print(df.head())
            
            # Save to CSV
            import os
            os.makedirs("data", exist_ok=True)
            df.to_csv("data/properties.csv", index=False)
            logger.info("Properties saved to data/properties.csv")
            
            # Save to Markdown
            markdown_file = save_to_markdown(df, config)
            logger.info(f"Markdown report saved to {markdown_file}")
            
            # Display summary statistics
            print(f"\n=== SUMMARY ===")
            print(f"Total properties found: {len(df)}")
            if 'price' in df.columns:
                print(f"Average price: ${df['price'].mean():,.2f}")
                print(f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
            
            # Show sample URLs
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