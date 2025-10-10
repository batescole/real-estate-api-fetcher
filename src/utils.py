import pandas as pd
import logging
from typing import Dict, List, Any, Optional
import urllib.parse

logger = logging.getLogger(__name__)

def clean_property_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize property data and remove duplicates"""
    if df.empty:
        return df
    
    original_count = len(df)
    
    # Convert price to numeric, removing any non-numeric characters
    df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
    
    # Convert numeric fields
    numeric_fields = ['beds', 'baths', 'sqft']
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce')
    
    # Clean address field
    df['address'] = df['address'].astype(str).str.strip()
    
    # Remove duplicates using multiple strategies
    df = remove_duplicates(df)
    
    final_count = len(df)
    duplicates_removed = original_count - final_count
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate properties")
    
    logger.info(f"Cleaned data: {final_count} properties after cleaning (removed {duplicates_removed} duplicates)")
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates using multiple strategies for robust duplicate detection"""
    if df.empty:
        return df
    
    original_count = len(df)
    
    # Strategy 1: Remove duplicates based on ZPID (most reliable)
    if 'zpid' in df.columns:
        df = df.drop_duplicates(subset=['zpid'], keep='first')
        logger.info(f"Removed duplicates by ZPID: {original_count} -> {len(df)}")
    
    # Strategy 2: Remove duplicates based on address + city + state combination
    address_cols = ['address', 'city', 'state']
    if all(col in df.columns for col in address_cols):
        # Create a copy to avoid pandas warnings
        df = df.copy()
        
        # Clean and normalize addresses for better matching
        df['address_normalized'] = df['address'].str.lower().str.strip()
        df['city_normalized'] = df['city'].str.lower().str.strip()
        df['state_normalized'] = df['state'].str.lower().str.strip()
        
        address_duplicates = df.duplicated(subset=['address_normalized', 'city_normalized', 'state_normalized'], keep='first')
        if address_duplicates.any():
            logger.info(f"Found {address_duplicates.sum()} address-based duplicates")
            df = df[~address_duplicates]
        
        # Clean up temporary columns
        df = df.drop(['address_normalized', 'city_normalized', 'state_normalized'], axis=1, errors='ignore')
    
    # Strategy 3: Remove duplicates based on property URL
    if 'property_url' in df.columns:
        url_duplicates = df.duplicated(subset=['property_url'], keep='first')
        if url_duplicates.any():
            logger.info(f"Found {url_duplicates.sum()} URL-based duplicates")
            df = df[~url_duplicates]
    
    # Strategy 4: Remove duplicates based on coordinates (for properties without ZPID)
    coord_cols = ['latitude', 'longitude']
    if all(col in df.columns for col in coord_cols):
        # Only check coordinates for rows without ZPID
        no_zpid_mask = df['zpid'].isna() | (df['zpid'] == '') | (df['zpid'] == 0)
        if no_zpid_mask.any():
            coord_subset = df[no_zpid_mask]
            coord_duplicates = coord_subset.duplicated(subset=['latitude', 'longitude'], keep='first')
            if coord_duplicates.any():
                logger.info(f"Found {coord_duplicates.sum()} coordinate-based duplicates")
                # Remove duplicates from the subset and update main dataframe
                duplicate_indices = coord_subset[coord_duplicates].index
                df = df.drop(duplicate_indices)
    
    final_count = len(df)
    total_removed = original_count - final_count
    
    if total_removed > 0:
        logger.info(f"Total duplicates removed: {total_removed} ({original_count} -> {final_count})")
    
    return df

def validate_no_duplicates(df: pd.DataFrame) -> bool:
    """Validate that no duplicates exist in the dataset"""
    if df.empty:
        return True
    
    # Check for ZPID duplicates
    if 'zpid' in df.columns:
        zpid_duplicates = df['zpid'].duplicated().sum()
        if zpid_duplicates > 0:
            logger.warning(f"Found {zpid_duplicates} ZPID duplicates after cleaning!")
            return False
    
    # Check for address duplicates
    address_cols = ['address', 'city', 'state']
    if all(col in df.columns for col in address_cols):
        address_duplicates = df.duplicated(subset=address_cols).sum()
        if address_duplicates > 0:
            logger.warning(f"Found {address_duplicates} address duplicates after cleaning!")
            return False
    
    # Check for URL duplicates
    if 'property_url' in df.columns:
        url_duplicates = df['property_url'].duplicated().sum()
        if url_duplicates > 0:
            logger.warning(f"Found {url_duplicates} URL duplicates after cleaning!")
            return False
    
    logger.info("No duplicates found in final dataset")
    return True

def filter_properties(df: pd.DataFrame, 
                     min_price: Optional[int] = None,
                     max_price: Optional[int] = None,
                     min_beds: Optional[int] = None,
                     max_beds: Optional[int] = None,
                     min_baths: Optional[int] = None,
                     min_sqft: Optional[int] = None,
                     max_sqft: Optional[int] = None,
                     propertyType: Optional[str] = None) -> pd.DataFrame:
    """Apply additional filters to property data"""
    if df.empty:
        return df
    
    original_count = len(df)
    
    if min_price is not None:
        df = df[df['price'] >= min_price]
    
    if max_price is not None:
        df = df[df['price'] <= max_price]
    
    if min_beds is not None:
        df = df[df['beds'] >= min_beds]
    
    if max_beds is not None:
        df = df[df['beds'] <= max_beds]
    
    if min_baths is not None:
        df = df[df['baths'] >= min_baths]
    
    if min_sqft is not None:
        df = df[df['sqft'] >= min_sqft]
    
    if max_sqft is not None:
        df = df[df['sqft'] <= max_sqft]
    
    if propertyType is not None:
        # Filter by property type (case-insensitive comparison)
        if 'propertyType' in df.columns:
            pre_filter_count = len(df)
            df = df[df['propertyType'].str.upper() == propertyType.upper()]
            filtered_count = pre_filter_count - len(df)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} properties not matching propertyType: {propertyType}")
    
    logger.info(f"Filtered data: {len(df)} properties remaining (from {original_count})")
    return df

def get_property_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate statistics from property data"""
    if df.empty:
        return {}
    
    stats = {
        'total_properties': len(df),
        'average_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'average_beds': df['beds'].mean(),
        'average_baths': df['baths'].mean(),
        'average_sqft': df['sqft'].mean(),
        'price_per_sqft_avg': df['price_per_sqft'].mean(),
        'cities': df['city'].value_counts().head(10).to_dict(),
        'propertyType': df['propertyType'].value_counts().to_dict()
    }
    
    return stats

def extract_zpid_from_url(url: str) -> Optional[str]:
    """Extract ZPID from Zillow property URL"""
    try:
        # Zillow URLs typically contain zpid in the format /zpid/
        if '/zpid/' in url:
            parts = url.split('/zpid/')
            if len(parts) > 1:
                zpid_part = parts[1].split('/')[0].split('_')[0]
                return zpid_part
        return None
    except Exception as e:
        logger.error(f"Error extracting ZPID from URL {url}: {e}")
        return None

def url_encode_property_url(url: str) -> str:
    """URL encode a property URL for API requests"""
    return urllib.parse.quote(url, safe='')

def save_to_csv(df: pd.DataFrame, filename: str, include_timestamp: bool = True) -> str:
    """Save DataFrame to CSV with optional timestamp"""
    import os
    from datetime import datetime
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
    
    filepath = os.path.join('data', filename)
    df.to_csv(filepath, index=False)
    logger.info(f"Data saved to {filepath}")
    return filepath

def load_from_csv(filename: str) -> pd.DataFrame:
    """Load DataFrame from CSV file"""
    import os
    filepath = os.path.join('data', filename)
    
    if not os.path.exists(filepath):
        logger.error(f"File {filepath} not found")
        return pd.DataFrame()
    
    df = pd.read_csv(filepath)
    logger.info(f"Loaded {len(df)} properties from {filepath}")
    return df

def compare_property_lists(old_df: pd.DataFrame, new_df: pd.DataFrame) -> Dict[str, List]:
    """Compare two property DataFrames to find new, removed, and changed properties"""
    if old_df.empty:
        return {
            'new_properties': new_df.to_dict('records'),
            'removed_properties': [],
            'price_changes': []
        }
    
    # Find new properties (in new_df but not in old_df)
    old_zpids = set(old_df['zpid'].astype(str))
    new_zpids = set(new_df['zpid'].astype(str))
    
    new_properties_zpids = new_zpids - old_zpids
    removed_properties_zpids = old_zpids - new_zpids
    
    new_properties = new_df[new_df['zpid'].astype(str).isin(new_properties_zpids)].to_dict('records')
    removed_properties = old_df[old_df['zpid'].astype(str).isin(removed_properties_zpids)].to_dict('records')
    
    # Find price changes for properties in both datasets
    common_zpids = old_zpids & new_zpids
    price_changes = []
    
    for zpid in common_zpids:
        old_price = old_df[old_df['zpid'].astype(str) == zpid]['price'].iloc[0]
        new_price = new_df[new_df['zpid'].astype(str) == zpid]['price'].iloc[0]
        
        if old_price != new_price:
            old_prop = old_df[old_df['zpid'].astype(str) == zpid].iloc[0].to_dict()
            new_prop = new_df[new_df['zpid'].astype(str) == zpid].iloc[0].to_dict()
            
            price_changes.append({
                'zpid': zpid,
                'address': new_prop.get('address', ''),
                'old_price': old_price,
                'new_price': new_price,
                'price_change': new_price - old_price,
                'price_change_pct': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
            })
    
    return {
        'new_properties': new_properties,
        'removed_properties': removed_properties,
        'price_changes': price_changes
    }
