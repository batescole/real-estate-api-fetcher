# real-estate-api-fetcher
Python tool to fetch real estate data by zip code using API

# Project Plan: Fetching Live Real Estate Data by Zip Code Using an API

## 1. Project Overview
### Objective
- Develop a Python script to fetch real-time real estate listings for specified zip codes using a public API.
- Parameters: Zip codes, min/max price, min/max bedrooms, min/max bathrooms, property type (e.g., single-family, condo), square footage, lot size, year built, and sorting (e.g., by price or date listed).
- Output: Structured data (JSON) with details like address, price, beds/baths, description, photos, and listing date.
- Handle pagination for multiple results.
- Daily deployment

### Scope
- In-scope: Data retrieval from one API (e.g., Zillow via Bridge Interactive or RapidAPI), parameter-based filtering, basic data cleaning, and storage in a local file/database.
- Out-of-scope: Advanced features like mapping visualizations, machine learning analysis, or a full web app UI (can be added in future phases). No handling of premium/paid listings beyond API access.

## 2. Technology Stack
- **Language:** Python
- **Libraries:**
  - Requests or HTTPX for API calls.
  - Pandas for data structuring/cleaning.
  - PyYAML for config file parsing.
  - Argparse or Click for command-line parameters.
  - SQLite or CSV for storage.
- **Tools:**
  - Git for version control.
  - Virtualenv or Poetry for dependency management.
  - Optional: Jupyter Notebook for prototyping.
- **Environment:** Local machine; no cloud deployment in initial phase.
- **API:** Zillow's GetSearchResults API (via Bridge Interactive) or RapidAPI's Zillow API wrapper.

## 3. Phase 1: Planning and Setup
### Steps:
1. **Research API:**
   - **Primary Choice:** Zillow's GetSearchResults API (requires free registration via Bridge Interactive or Zillow's developer portal).
     - Endpoint example: `https://api.bridgedataoutput.com/api/v2/zillow_listings?access_token={API_KEY}&zip={ZIP_CODE}`.
     - Parameters: Supports zip code, price range, beds/baths, property type, etc.
   - **Alternative:** RapidAPI's Zillow API (e.g., `https://zillow-com1.p.rapidapi.com/search`).
   - Sign up for API key: Register at [Bridge Interactive](https://developers.zillow.com/) or [RapidAPI](https://rapidapi.com/).
   - Review documentation: Check rate limits (e.g., 1000 calls/day for Zillow free tier), required fields, and response format.

2. **Define Parameters:**
   - Create a config file (config.yaml) with defaults:
     ```yaml
     api_key: "your_api_key_here"
     curl --request GET 
	  --url 'https://zillow-com1.p.rapidapi.com/property3dtour?property_url=https%3A%2F%2Fwww.zillow.com%2Fhomedetails%2F1541-SW-102nd-Ter-Davie-FL-33324%2F43177112_zpid' 
	  --header 'x-rapidapi-host: zillow-com1.p.rapidapi.com' 
	  --header 'x-rapidapi-key: 1c1c20660cmshb9de78075042139p1d134cjsn83640c308aec'
     zip_codes: ["37415", "37341 to 37450"]
     min_price: 150000
     max_price: 300000
     min_beds: 2
     min_baths: 1
     property_types: ["house", "foreclosure"]
     sort_by: "newest"
