#!/bin/bash

# Script to push markdown reports to GitHub
# This should be run after the daily_runner.py completes

PROJECT_DIR=$(pwd)
TIMESTAMP=$(date +"%Y%m%d")

echo "Pushing daily property report to GitHub..."

# Navigate to project directory
cd "$PROJECT_DIR"

# Find the latest markdown report (macOS compatible)
LATEST_REPORT=$(find data/ -name "properties_report_*.md" -type f -exec stat -f "%m %N" {} \; | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$LATEST_REPORT" ]; then
    echo "No markdown report found in data/ directory"
    exit 1
fi

echo "Found report: $LATEST_REPORT"

# Copy the latest report to a standard name for GitHub
cp "$LATEST_REPORT" "daily_property_report.md"

# Add and commit the report
git add daily_property_report.md
git commit -m "Daily property report update - $TIMESTAMP"

# Push to GitHub
git push origin main

if [ $? -eq 0 ]; then
    echo "Successfully pushed daily report to GitHub"
else
    echo "Failed to push to GitHub"
    exit 1
fi
