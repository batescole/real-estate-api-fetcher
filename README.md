# Real Estate API Fetcher

A Python application that fetches real estate property data from Bridge Interactive API and generates formatted reports.

## Features

- **Property Search**: Search properties with customizable filters
- **Bridge API Integration**: Uses Bridge Interactive MLS data API
- **Multiple Output Formats**: CSV data files and formatted Markdown reports
- **Secure Configuration**: Keeps API access tokens local, code on GitHub

## Requirements

- Python 3.7+
- Bridge Interactive API access token
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
   cp config.yaml.template config.yaml
   # Edit config.yaml with your Bridge API access token and search parameters
   ```

## Usage

Run the fetcher from command line:
```bash
source venv/bin/activate
python src/fetcher.py
```

## Output Files

The application generates files in the `data/` directory:

- **`properties.csv`** - Raw property data
- **`properties_report_YYYYMMDD_HHMMSS.md`** - Formatted markdown report with timestamp
- **`daily_property_report.md`** - Latest property report for GitHub tracking

## Security & Privacy

- **API Access Token**: Stored locally in `config.yaml` (not committed to GitHub)
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
├── daily_property_report.md # Latest report (tracked in git)
└── requirements.txt        # Python dependencies
```
