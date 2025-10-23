#!/bin/bash

echo "============================================"
echo "Starting Migrion - ERP Data Migration Platform"
echo "============================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and add your API keys"
    echo ""
    exit 1
fi

echo "Starting Streamlit application..."
echo "Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
