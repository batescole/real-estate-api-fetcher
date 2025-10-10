# Real Estate API Fetcher

A Python application that fetches real estate property data from Zillow using RapidAPI and generates formatted reports.

## Features

- **Property Search**: Search properties by zip code with customizable filters
- **RapidAPI Integration**: Uses Zillow API through RapidAPI
- **Multiple Output Formats**: CSV data files and formatted Markdown reports
- **Daily Automation**: Automated daily fetching with cron job support
- **Change Tracking**: Detects new, removed, and price-changed properties
- **Secure Configuration**: Keeps API keys local, code on GitHub

## Requirements

- Python 3.7+
- RapidAPI account with Zillow API access
- Virtual environment (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/real-estate-api-fetcher.git
   cd real-estate-api-fetcher
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API access**:
   ```bash
   cp config.yaml
   # Edit config.yaml with your API key and search parameters
   ```

## Output Files

The application generates several output files in the `data/` directory:

- **`properties_YYYYMMDD_HHMMSS.csv`** - Raw property data
- **`properties_report_YYYYMMDD_HHMMSS.md`** - Formatted markdown report
- **`daily_runner.log`** - Execution logs
- **`cron.log`** - Cron job logs (if using automation)


## Daily Automation

The daily runner provides:

- **Incremental Updates**: Updates existing reports instead of creating new ones
- **Change Detection**: Tracks new, removed, and price-changed properties
- **Historical Data**: Maintains CSV files with timestamps for comparison
- **Error Handling**: Comprehensive logging and error recovery
- **Cron Scheduling**: Automated scripts ran Daily @ 9AM

## Security & Privacy

- **API Keys**: Stored locally in `config.yaml` (not committed to GitHub)
- **Data Files**: All property data stays on your local machine

## Project Structure

```
real-estate-api-fetcher/
├── src/
│   ├── fetcher.py          # Main API client and fetching logic
│   └── utils.py            # Utility functions for data processing
├── data/                   # Output directory (local only)
├── venv/                   # Virtual environment (local only)
├── config.yaml             # Your API configuration (local only)
├── config.yaml.template    # Template for GitHub
├── daily_runner.py         # Daily automation script
├── test_daily.py           # Test script
├── setup_cron.sh           # Cron job setup script
└── requirements.txt        # Python dependencies
```

## Development
### API Endpoints Used

- `propertyExtendedSearch` - Search for properties by location and filters
- `property` - Get detailed property information by ZPID
- `propertyByUrl` - Get property details from Zillow URL
