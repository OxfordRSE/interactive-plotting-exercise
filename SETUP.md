# Setup Instructions

## Running the Application

1. **Start the local server:**
   ```bash
   python -m http.server 8000
   ```
   Or alternatively:
   ```bash
   npm start
   ```

2. **Open your browser:**
   Navigate to `http://localhost:8000`

## Features

- **Interactive Map:** Click on colored circles to see regional carbon intensity data
- **Time Controls:** Use the datetime picker to view historical data (rounded to nearest 30 minutes)
- **Region Details:** Selected region shows intensity, generation mix, and DNO information
- **Time Series:** View 24-hour carbon intensity trends for selected regions
- **Color Legend:** Visual indication of carbon intensity levels

## API Endpoints Used

- Current regional data: `https://api.carbonintensity.org.uk/regional`
- Historical data: `https://api.carbonintensity.org.uk/regional/intensity/{from}/{to}`
- Region-specific time series: `https://api.carbonintensity.org.uk/regional/intensity/{from}/{to}/regionid/{id}`

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Mapping:** Leaflet.js
- **Visualization:** D3.js
- **API:** UK Carbon Intensity API

## File Structure

- `index.html` - Main HTML structure
- `style.css` - Styling and responsive design
- `app.js` - Main application logic and API integration
- `package.json` - Project metadata and dependencies