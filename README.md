# 🏠 Real Estate API Fetcher

A Python application that fetches real estate property data from Zillow using RapidAPI and generates formatted reports.

## 🚀 Features

- **Property Search**: Search properties by zip code with customizable filters
- **RapidAPI Integration**: Uses Zillow API through RapidAPI
- **Multiple Output Formats**: CSV data files and formatted Markdown reports
- **Daily Automation**: Automated daily fetching with cron job support
- **Change Tracking**: Detects new, removed, and price-changed properties
- **Secure Configuration**: Keeps API keys local, code on GitHub

## 📋 Requirements

- Python 3.7+
- RapidAPI account with Zillow API access
- Virtual environment (recommended)

## 🛠️ Installation

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
   # Edit config.yaml with your API key and search parameters
   ```

## ⚙️ Configuration

Edit `config.yaml` with your settings:

```yaml
api_key: "your_rapidapi_key_here"
host: "zillow-com1.p.rapidapi.com"

# Search parameters
zip_codes: ["37415", "37405", "37409"]
min_price: 150000
max_price: 300000
min_beds: 2
min_baths: 1
property_types: ["house"]
sort_by: "newest"
```

### 🔑 Getting Your RapidAPI Key

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to the [Zillow API](https://rapidapi.com/s.mahmoud97/api/zillow-com1/)
3. Copy your API key from the dashboard
4. Add it to your local `config.yaml` file

## 🏃‍♂️ Usage

### One-Time Run
```bash
python src/fetcher.py
```

### Test Daily Runner
```bash
python test_daily.py
```

### Set Up Daily Automation
```bash
./setup_cron.sh
```

## 📊 Output Files

The application generates several output files in the `data/` directory:

- **`properties_YYYYMMDD_HHMMSS.csv`** - Raw property data
- **`properties_report_YYYYMMDD_HHMMSS.md`** - Formatted markdown report
- **`daily_runner.log`** - Execution logs
- **`cron.log`** - Cron job logs (if using automation)

## 📝 Sample Markdown Report

```markdown
# Real Estate Property Report
**Last Updated:** 2024-01-15 09:00:25

## Search Criteria
- **Zip Codes:** 37415, 37405, 37409
- **Price Range:** $150,000 - $300,000
- **Minimum Beds:** 2

## Property Listings

### 1. 123 Main St, Chattanooga, TN
**Price:** $245,000
**Bedrooms/Bathrooms:** 3/2
**Square Feet:** 1,850
**Zillow Link:** [View Property](https://www.zillow.com/...)
```

## 🔄 Daily Automation

The daily runner provides:

- **Incremental Updates**: Updates existing reports instead of creating new ones
- **Change Detection**: Tracks new, removed, and price-changed properties
- **Historical Data**: Maintains CSV files with timestamps for comparison
- **Error Handling**: Comprehensive logging and error recovery

### Setting Up Cron Job

Run the setup script:
```bash
./setup_cron.sh
```

This will:
- Check your virtual environment
- Generate the appropriate cron command
- Provide instructions for setting up the daily job

The default schedule runs daily at 9:00 AM.

## 🔒 Security & Privacy

- **API Keys**: Stored locally in `config.yaml` (not committed to GitHub)
- **Data Files**: All property data stays on your local machine
- **Template Config**: `config.yaml.template` provides a safe template for GitHub

## 📁 Project Structure

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

## 🛠️ Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_daily.py`
5. Submit a pull request

### API Endpoints Used

- `propertyExtendedSearch` - Search for properties by location and filters
- `property` - Get detailed property information by ZPID
- `propertyByUrl` - Get property details from Zillow URL

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your RapidAPI key is correct and has sufficient quota
2. **No Properties Found**: Check your search criteria (price range, zip codes)
3. **Permission Errors**: Make sure the `data/` directory is writable
4. **Cron Job Not Running**: Check cron logs and ensure paths are correct

### Debug Mode

Enable debug logging by modifying the logging level in the scripts:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the logs in the `data/` directory
3. Open an issue on GitHub

---

**Note**: This application is for personal use and educational purposes. Please respect Zillow's terms of service and API rate limits.