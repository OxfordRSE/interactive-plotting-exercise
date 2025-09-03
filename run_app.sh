#!/bin/bash
# UK Carbon Intensity App Launcher

echo "🌱 Starting UK Carbon Intensity Mapping Application..."
echo "Using Python $(python --version)"
echo ""

# Activate virtual environment and run app
source carbon_intensity_env/bin/activate
echo "" | streamlit run carbon_intensity_app.py --server.headless=true

echo ""
echo "Application stopped."