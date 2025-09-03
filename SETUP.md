# Setup Instructions

## Running the Python Application

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run carbon_intensity_app.py
   ```

3. **Open your browser:**
   The app will be available at one of these URLs (check the terminal output):
   - `http://localhost:8501` (if running locally)
   - `http://192.168.x.x:8501` (network URL)
   
   **Alternative:** Run with the launcher script:
   ```bash
   ./run_app.sh
   ```

## Troubleshooting

- **Email prompt on first run:** Just press Enter to skip
- **Port already in use:** Streamlit will automatically find another port
- **App not loading:** Check the terminal output for the correct URL
- **Permission denied:** Run `chmod +x run_app.sh` first

## Features

- **Interactive Map:** Click on colored circles to see regional carbon intensity data
- **Time Controls:** Toggle between current time or select historical data
- **Region Details:** Selected region shows intensity, generation mix, and DNO information  
- **Time Series:** Click "Load Time Series" to view 24-hour carbon intensity trends
- **Color-coded Visualization:** Visual indication of carbon intensity levels

## API Endpoints Used

- Current regional data: `https://api.carbonintensity.org.uk/regional`
- Historical data: `https://api.carbonintensity.org.uk/regional/intensity/{from}/{to}`
- Region-specific time series: `https://api.carbonintensity.org.uk/regional/intensity/{from}/{to}/regionid/{id}`

## Technology Stack

- **Framework:** Streamlit
- **Mapping:** Folium with streamlit-folium
- **Visualization:** Plotly Express
- **Data Processing:** Pandas
- **API Requests:** Requests library

## File Structure

- `carbon_intensity_app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `README.md` - Exercise instructions