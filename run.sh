#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Fetch the latest data using weather_data.py
echo "Fetching the latest data..."
python weather_data.py fetch

# Run the application using Streamlit
echo "Starting the application with Streamlit..."
streamlit run app.py
