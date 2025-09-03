import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="UK Carbon Intensity Map",
    page_icon="🌱",
    layout="wide"
)

class CarbonIntensityAPI:
    """Class to handle UK Carbon Intensity API calls"""
    
    BASE_URL = "https://api.carbonintensity.org.uk"
    
    @staticmethod
    def get_current_regional_data():
        """Fetch current regional carbon intensity data"""
        try:
            response = requests.get(f"{CarbonIntensityAPI.BASE_URL}/regional")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching current data: {e}")
            return None
    
    @staticmethod
    def get_historical_regional_data(from_date, to_date):
        """Fetch historical regional data for a date range"""
        try:
            from_str = from_date.strftime("%Y-%m-%dT%H:%M") + "Z"
            to_str = to_date.strftime("%Y-%m-%dT%H:%M") + "Z"
            response = requests.get(f"{CarbonIntensityAPI.BASE_URL}/regional/intensity/{from_str}/{to_str}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching historical data: {e}")
            return None
    
    @staticmethod
    def get_region_time_series(region_id, from_date, to_date):
        """Fetch time series data for a specific region"""
        try:
            from_str = from_date.strftime("%Y-%m-%dT%H:%M") + "Z"
            to_str = to_date.strftime("%Y-%m-%dT%H:%M") + "Z"
            response = requests.get(f"{CarbonIntensityAPI.BASE_URL}/regional/intensity/{from_str}/{to_str}/regionid/{region_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching time series data: {e}")
            return None

class RegionMapper:
    """Class to handle region coordinates and mapping"""
    
    # Approximate coordinates for UK regions
    REGION_COORDINATES = {
        1: [58.0, -4.5],    # North Scotland
        2: [55.5, -3.5],    # South Scotland
        3: [54.0, -2.5],    # North West England
        4: [55.0, -1.5],    # North East England
        5: [54.0, -1.0],    # Yorkshire
        6: [53.0, -3.0],    # North Wales & Merseyside
        7: [51.5, -3.5],    # South Wales
        8: [52.5, -2.0],    # West Midlands
        9: [52.8, -1.0],    # East Midlands
        10: [52.5, 0.5],    # East England
        11: [50.5, -3.5],   # South West England
        12: [51.0, -1.0],   # South England
        13: [51.5, -0.1],   # London
        14: [51.2, 0.5],    # South East England
    }
    
    @staticmethod
    def get_intensity_color(intensity):
        """Get color based on carbon intensity level"""
        if intensity <= 50:
            return 'green'      # Very Low
        elif intensity <= 100:
            return 'lightgreen' # Low
        elif intensity <= 200:
            return 'orange'     # Moderate
        elif intensity <= 300:
            return 'red'        # High
        else:
            return 'darkred'    # Very High
    
    @staticmethod
    def get_intensity_index(intensity):
        """Get intensity index category"""
        if intensity <= 50:
            return 'Very Low'
        elif intensity <= 100:
            return 'Low'
        elif intensity <= 200:
            return 'Moderate'
        elif intensity <= 300:
            return 'High'
        else:
            return 'Very High'

def create_map(regions_data):
    """Create a Folium map with regional data"""
    # Center map on UK
    uk_map = folium.Map(location=[54.5, -3], zoom_start=6)
    
    if not regions_data or 'regions' not in regions_data:
        return uk_map
    
    for region in regions_data['regions']:
        # Skip country-level aggregations
        if region['regionid'] > 14:
            continue
            
        coords = RegionMapper.REGION_COORDINATES.get(region['regionid'], [54.0, -2.0])
        intensity = region['intensity']['forecast']
        color = RegionMapper.get_intensity_color(intensity)
        
        # Create popup content
        popup_text = f"""
        <b>{region['shortname']}</b><br>
        Intensity: {intensity} gCO₂/kWh<br>
        Index: {RegionMapper.get_intensity_index(intensity)}<br>
        DNO: {region['dnoregion']}
        """
        
        # Add marker to map
        folium.CircleMarker(
            location=coords,
            radius=15,
            popup=folium.Popup(popup_text, max_width=300),
            color='white',
            weight=2,
            fillColor=color,
            fillOpacity=0.8,
            tooltip=f"{region['shortname']}: {intensity} gCO₂/kWh"
        ).add_to(uk_map)
    
    return uk_map

def create_time_series_chart(time_series_data, region_name):
    """Create a time series chart using Plotly"""
    if not time_series_data or 'data' not in time_series_data:
        return None
    
    data_points = time_series_data['data']['data']
    
    # Prepare data for plotting
    timestamps = []
    intensities = []
    
    for point in data_points:
        timestamps.append(datetime.fromisoformat(point['from'].replace('Z', '+00:00')))
        intensities.append(point['intensity']['forecast'])
    
    # Create DataFrame
    df = pd.DataFrame({
        'Time': timestamps,
        'Carbon Intensity (gCO₂/kWh)': intensities
    })
    
    # Create Plotly line chart
    fig = px.line(
        df,
        x='Time',
        y='Carbon Intensity (gCO₂/kWh)',
        title=f'Carbon Intensity Time Series - {region_name} (Last 24 Hours)',
        line_shape='linear'
    )
    
    # Add color coding based on intensity levels
    colors = [RegionMapper.get_intensity_color(i) for i in intensities]
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=6, color=colors[0] if colors else 'blue')
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Carbon Intensity (gCO₂/kWh)",
        hovermode='x unified'
    )
    
    return fig

def display_region_details(region):
    """Display detailed information about a selected region"""
    st.subheader(f"📍 {region['shortname']}")
    
    intensity = region['intensity']['forecast']
    color = RegionMapper.get_intensity_color(intensity)
    index = RegionMapper.get_intensity_index(intensity)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Carbon Intensity", f"{intensity} gCO₂/kWh", delta=None)
        st.write(f"**Index:** {index}")
        st.write(f"**DNO Region:** {region['dnoregion']}")
    
    with col2:
        # Generation Mix
        if 'generationmix' in region and region['generationmix']:
            st.write("**Generation Mix:**")
            gen_data = {fuel['fuel'].title(): fuel['perc'] for fuel in region['generationmix'] if fuel['perc'] > 0}
            
            if gen_data:
                # Create a simple bar chart for generation mix
                fig = px.bar(
                    x=list(gen_data.keys()),
                    y=list(gen_data.values()),
                    title="Energy Generation Mix (%)",
                    labels={'x': 'Fuel Type', 'y': 'Percentage (%)'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

def round_to_nearest_half_hour(dt):
    """Round datetime to nearest 30 minutes"""
    minutes = dt.minute
    rounded_minutes = 0 if minutes < 30 else 30
    return dt.replace(minute=rounded_minutes, second=0, microsecond=0)

def main():
    st.title("🌱 UK Carbon Intensity Map")
    st.markdown("Interactive visualization of carbon intensity across UK regions")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Controls")
    
    # Time selection
    use_current_time = st.sidebar.checkbox("Use current time", value=True)
    
    if use_current_time:
        selected_datetime = datetime.now()
    else:
        selected_date = st.sidebar.date_input("Select date", datetime.now().date())
        selected_time = st.sidebar.time_input("Select time", datetime.now().time())
        selected_datetime = datetime.combine(selected_date, selected_time)
    
    # Round to nearest half hour
    selected_datetime = round_to_nearest_half_hour(selected_datetime)
    
    st.sidebar.write(f"**Selected time:** {selected_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    # Fetch and display data
    if use_current_time:
        data = CarbonIntensityAPI.get_current_regional_data()
        if data and 'data' in data and len(data['data']) > 0:
            regions_data = data['data'][0]
        else:
            regions_data = None
    else:
        # For historical data, we need a time range
        to_datetime = selected_datetime + timedelta(minutes=30)
        data = CarbonIntensityAPI.get_historical_regional_data(selected_datetime, to_datetime)
        if data and 'data' in data and len(data['data']) > 0:
            regions_data = data['data'][0]
        else:
            regions_data = None
    
    if regions_data is None:
        st.error("Failed to load regional data. Please try again.")
        return
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Regional Carbon Intensity Map")
        
        # Create and display map
        uk_map = create_map(regions_data)
        map_data = st_folium(uk_map, width=700, height=500, returned_objects=["last_object_clicked"])
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟢 Very Low (0-50 gCO₂/kWh)
        - 🟢 Low (51-100 gCO₂/kWh)  
        - 🟠 Moderate (101-200 gCO₂/kWh)
        - 🔴 High (201-300 gCO₂/kWh)
        - 🔴 Very High (300+ gCO₂/kWh)
        """)
    
    with col2:
        st.subheader("📊 Region Details")
        
        # Get clicked region information
        clicked_region = None
        if map_data['last_object_clicked']:
            # Find the region based on coordinates (approximate match)
            clicked_coords = map_data['last_object_clicked']['lat'], map_data['last_object_clicked']['lng']
            
            for region in regions_data['regions']:
                if region['regionid'] <= 14:  # Skip country aggregations
                    region_coords = RegionMapper.REGION_COORDINATES.get(region['regionid'])
                    if region_coords:
                        # Simple distance check (within reasonable range)
                        if (abs(clicked_coords[0] - region_coords[0]) < 1.0 and 
                            abs(clicked_coords[1] - region_coords[1]) < 1.0):
                            clicked_region = region
                            break
        
        if clicked_region:
            display_region_details(clicked_region)
            
            # Time series section
            st.subheader("📈 Time Series Analysis")
            
            if st.button("Load Time Series (Last 24 Hours)", type="primary"):
                with st.spinner("Loading time series data..."):
                    end_time = datetime.now()
                    start_time = end_time - timedelta(hours=24)
                    
                    time_series_data = CarbonIntensityAPI.get_region_time_series(
                        clicked_region['regionid'], start_time, end_time
                    )
                    
                    if time_series_data:
                        fig = create_time_series_chart(time_series_data, clicked_region['shortname'])
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No time series data available for this region.")
                    else:
                        st.error("Failed to load time series data.")
        else:
            st.info("👆 Click on a region marker on the map to see details and time series data.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Source:** [UK Carbon Intensity API](https://carbonintensity.org.uk/)  
    **Last Updated:** Real-time data from National Grid ESO
    """)

if __name__ == "__main__":
    main()