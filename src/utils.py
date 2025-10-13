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
        if 'propertySubType' in df.columns:
            pre_filter_count = len(df)
            df = df[df['propertySubType'].str.contains(propertyType, case=False, na=False)]
            filtered_count = pre_filter_count - len(df)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} properties not matching propertyType: {propertyType}")
    
    logger.info(f"Filtered data: {len(df)} properties remaining (from {original_count})")
    return df
