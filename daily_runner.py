#!/usr/bin/env python3
"""
Daily runner script for real estate property fetching
Handles incremental updates to markdown reports
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fetcher import ZillowRapidAPIClient, load_config, search_properties_by_zip_codes
from utils import compare_property_lists, load_from_csv, save_to_csv, clean_property_data, validate_no_duplicates
import logging
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/daily_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_previous_data():
    """Load previous day's data for comparison"""
    try:
        # Look for the most recent CSV file
        import glob
        csv_files = glob.glob("data/properties_*.csv")
        if not csv_files:
            return None
        
        # Get the most recent file
        latest_file = max(csv_files, key=os.path.getctime)
        logger.info(f"Loading previous data from: {latest_file}")
        return load_from_csv(os.path.basename(latest_file))
    except Exception as e:
        logger.error(f"Error loading previous data: {e}")
        return None

def update_markdown_report(new_df, config, changes=None):
    """Update the markdown report with new data and changes"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Check if we have an existing report to update
    import glob
    existing_reports = glob.glob("data/properties_report_*.md")
    
    if existing_reports and not changes:
        # Just update the existing report with new data
        latest_report = max(existing_reports, key=os.path.getctime)
        logger.info(f"Updating existing report: {latest_report}")
        return update_existing_report(latest_report, new_df, config)
    else:
        # Create a new report (first run or significant changes)
        return create_new_report(new_df, config, changes)

def update_existing_report(report_path, new_df, config):
    """Update an existing markdown report with new data"""
    try:
        # Read existing content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the end of the summary section
        summary_end = content.find("## Property Listings")
        
        if summary_end == -1:
            # If no property listings section, create new report
            return create_new_report(new_df, config)
        
        # Keep header and summary, replace property listings
        header_content = content[:summary_end]
        
        # Generate new property listings
        property_listings = generate_property_listings(new_df)
        
        # Combine and write
        new_content = header_content + "\n" + property_listings
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Update the last modified timestamp in header
        update_report_timestamp(report_path)
        
        logger.info(f"Updated existing report: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"Error updating existing report: {e}")
        return create_new_report(new_df, config)

def update_report_timestamp(report_path):
    """Update the timestamp in the report header"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and update the timestamp line
        for i, line in enumerate(lines):
            if "**Generated on:**" in line or "**Last Updated:**" in line:
                lines[i] = f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                break
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
    except Exception as e:
        logger.error(f"Error updating timestamp: {e}")

def create_new_report(new_df, config, changes=None):
    """Create a new markdown report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"properties_report_{timestamp}.md"
    filepath = os.path.join("data", filename)
    
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
    if not new_df.empty:
        markdown_content.append("## Summary Statistics")
        markdown_content.append(f"- **Total Properties Found:** {len(new_df)}")
        
        if 'price' in new_df.columns:
            avg_price = new_df['price'].mean()
            min_price = new_df['price'].min()
            max_price = new_df['price'].max()
            markdown_content.append(f"- **Average Price:** ${avg_price:,.2f}")
            markdown_content.append(f"- **Price Range:** ${min_price:,.0f} - ${max_price:,.0f}")
        
        markdown_content.append("")
    
    # Changes section if there are changes
    if changes:
        markdown_content.append("## Recent Changes")
        markdown_content.append(f"- **New Properties:** {len(changes.get('new_properties', []))}")
        markdown_content.append(f"- **Removed Properties:** {len(changes.get('removed_properties', []))}")
        markdown_content.append(f"- **Price Changes:** {len(changes.get('price_changes', []))}")
        markdown_content.append("")
    
    # Property listings
    property_listings = generate_property_listings(new_df)
    markdown_content.append(property_listings)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_content))
    
    logger.info(f"Created new report: {filepath}")
    return filepath

def generate_property_listings(df):
    """Generate the property listings section of markdown"""
    if df.empty:
        return "## No Properties Found\nNo properties were found matching your search criteria."
    
    content = ["## Property Listings", ""]
    
    for idx, row in df.iterrows():
        # Property header (address only)
        address = row.get('address', 'N/A')
        content.append(f"### {idx + 1}. {address}")
        
        # Property details
        price = row.get('price', 0)
        if price > 0:
            content.append(f"**Price:** ${price:,}")
        
        beds = row.get('beds', 0)
        baths = row.get('baths', 0)
        if beds > 0 or baths > 0:
            content.append(f"**Bedrooms/Bathrooms:** {beds}/{baths}")
        
        sqft = row.get('sqft', 0)
        if sqft > 0:
            content.append(f"**Square Feet:** {sqft:,}")
        
        """NOT GETTING PROPERTY TYPE"""
        property_type = row.get('property_type', '')
        if property_type:
            content.append(f"**Property Type:** {property_type}")
        else:
            content.append("**Property Type:** Not available")

        content.append("")
        
        # Zillow URL on its own line
        # NEED TO CONCAT ZILLOW.COM
        property_url = row.get('property_url', '')
        if property_url:
            content.append(f"**URL:** www.zillow.com{property_url}")
        
        content.append("")
    
    return '\n'.join(content)

def run_daily_fetch():
    """Main function to run daily property fetching"""
    try:
        logger.info("Starting daily property fetch...")
        
        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration for zip codes: {config['zip_codes']}")
        
        # Initialize client
        client = ZillowRapidAPIClient(
            api_key=config["api_key"],
            host=config["host"]
        )
        
        # Search parameters from config
        search_params = {
            "min_price": config.get("min_price"),
            "max_price": config.get("max_price"),
            "min_beds": config.get("min_beds"),
            "min_baths": config.get("min_baths"),
            "property_types": config.get("property_types"),
            "sort_by": config.get("sort_by")
        }
        
        # Fetch new data
        new_df = search_properties_by_zip_codes(
            client=client,
            zip_codes=config["zip_codes"],
            search_params=search_params
        )
        
        if new_df.empty:
            logger.warning("No properties found in today's search")
            return
        
        logger.info(f"Found {len(new_df)} properties before duplicate removal")
        
        # Clean data and remove duplicates
        new_df = clean_property_data(new_df)
        
        if new_df.empty:
            logger.warning("No properties remaining after duplicate removal")
            return
        
        logger.info(f"Found {len(new_df)} unique properties after cleaning")
        
        # Validate no duplicates exist
        if not validate_no_duplicates(new_df):
            logger.error("Duplicate validation failed! Please check the data.")
        
        # Load previous data for comparison
        old_df = load_previous_data()
        
        # Compare data and detect changes
        changes = None
        if old_df is not None and not old_df.empty:
            changes = compare_property_lists(old_df, new_df)
            logger.info(f"Changes detected - New: {len(changes['new_properties'])}, "
                       f"Removed: {len(changes['removed_properties'])}, "
                       f"Price changes: {len(changes['price_changes'])}")
        
        # Save new data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"properties_{timestamp}.csv"
        save_to_csv(new_df, csv_filename, include_timestamp=False)
        
        # Update markdown report
        markdown_file = update_markdown_report(new_df, config, changes)
        
        logger.info(f"Daily fetch completed successfully. Report: {markdown_file}")
        
        # Push to GitHub
        try:
            import subprocess
            result = subprocess.run(['./push_to_github.sh'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                logger.info("Successfully pushed report to GitHub")
            else:
                logger.warning(f"GitHub push failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Failed to push to GitHub: {e}")
        
        # Log summary
        logger.info(f"Summary - Total properties: {len(new_df)}, "
                   f"Average price: ${new_df['price'].mean():,.2f}")
        
    except Exception as e:
        logger.error(f"Error in daily fetch: {e}")
        raise

if __name__ == "__main__":
    run_daily_fetch()
