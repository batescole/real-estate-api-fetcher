#!/bin/bash

# Setup script for daily real estate property fetching
# This script helps you set up a cron job to run daily

echo "Real Estate API Fetcher - Daily Cron Setup"
echo "============================================"
echo "This setup is for LOCAL EXECUTION only"
echo "Your API keys and data will stay on your local machine"
echo "Code can be pushed to GitHub without sensitive data"
echo ""

# Get the current directory
PROJECT_DIR=$(pwd)
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/daily_runner.py"

echo "Project directory: $PROJECT_DIR"
echo "Python path: $PYTHON_PATH"
echo "Script path: $SCRIPT_PATH"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "ERROR: Virtual environment not found at $PYTHON_PATH"
    echo "Please run 'python3 -m venv venv' and 'source venv/bin/activate' first"
    exit 1
fi

# Check if the daily runner script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: Daily runner script not found at $SCRIPT_PATH"
    exit 1
fi

echo ""
echo "All files found. Setting up cron job..."

# Create a temporary cron file
CRON_FILE="/tmp/real_estate_cron"
echo "# Real Estate API Fetcher - Daily run at 9:00 AM with GitHub push" > $CRON_FILE
echo "0 9 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $PROJECT_DIR/data/cron.log 2>&1" >> $CRON_FILE

echo ""
echo "Cron job to be added:"
echo "Time: 9:00 AM daily"
echo "Command: cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH"
echo "Log file: $PROJECT_DIR/data/cron.log"
echo ""

# Show current crontab
echo "Current crontab:"
crontab -l 2>/dev/null || echo "No crontab found"

echo ""
echo "To add this cron job, run one of these commands:"
echo ""
echo "Option 1 - Add to existing crontab:"
echo "  crontab -e"
echo "  # Then add this line:"
echo "  0 9 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $PROJECT_DIR/data/cron.log 2>&1"
echo ""
echo "Option 2 - Replace crontab (WARNING: This will replace ALL existing cron jobs):"
echo "  crontab $CRON_FILE"
echo ""
echo "Option 3 - Test run first:"
echo "  $PYTHON_PATH $SCRIPT_PATH"
echo ""

# Make the script executable
chmod +x "$SCRIPT_PATH"
echo "Made daily_runner.py executable"

# Create data directory if it doesn't exist
mkdir -p "$PROJECT_DIR/data"
echo "Created data directory"

echo ""
echo "Next steps:"
echo "1. Test the script: $PYTHON_PATH $SCRIPT_PATH"
echo "2. Set up cron job using one of the options above"
echo "3. Check logs in: $PROJECT_DIR/data/"
echo ""
echo "The script will:"
echo "- Fetch properties daily at 9:00 AM"
echo "- Update the markdown report with new data"
echo "- Track changes (new/removed/price changes)"
echo "- Save data to CSV files with timestamps"
echo "- Push daily report to GitHub"
echo "- Log all activity to data/daily_runner.log"
