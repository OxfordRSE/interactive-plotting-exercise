class CarbonIntensityApp {
    constructor() {
        this.map = null;
        this.regionMarkers = [];
        this.currentData = null;
        this.selectedRegion = null;
        this.init();
    }

    async init() {
        this.initMap();
        this.initControls();
        await this.loadCurrentData();
        this.updateMap();
    }

    initMap() {
        // Initialize Leaflet map centered on UK
        this.map = L.map('map').setView([54.5, -3], 6);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    initControls() {
        // Set current datetime
        const now = new Date();
        const datetimeInput = document.getElementById('datetime');
        datetimeInput.value = now.toISOString().slice(0, 16);

        // Now button event
        document.getElementById('now-btn').addEventListener('click', () => {
            const now = new Date();
            datetimeInput.value = now.toISOString().slice(0, 16);
            this.loadCurrentData();
        });

        // Datetime change event
        datetimeInput.addEventListener('change', () => {
            this.loadHistoricalData(new Date(datetimeInput.value));
        });
    }

    async loadCurrentData() {
        try {
            const response = await fetch('https://api.carbonintensity.org.uk/regional');
            const data = await response.json();
            this.currentData = data.data[0];
            this.updateMap();
        } catch (error) {
            console.error('Error loading current data:', error);
        }
    }

    async loadHistoricalData(dateTime) {
        try {
            // Round to nearest 30 minutes
            const roundedDate = this.roundToNearestHalfHour(dateTime);
            const from = roundedDate.toISOString().slice(0, -5) + 'Z';
            const to = new Date(roundedDate.getTime() + 30 * 60 * 1000).toISOString().slice(0, -5) + 'Z';
            
            const response = await fetch(`https://api.carbonintensity.org.uk/regional/intensity/${from}/${to}`);
            const data = await response.json();
            
            if (data.data && data.data.length > 0) {
                this.currentData = data.data[0];
                this.updateMap();
            }
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    }

    roundToNearestHalfHour(date) {
        const minutes = date.getMinutes();
        const roundedMinutes = minutes < 30 ? 0 : 30;
        const roundedDate = new Date(date);
        roundedDate.setMinutes(roundedMinutes);
        roundedDate.setSeconds(0);
        roundedDate.setMilliseconds(0);
        return roundedDate;
    }

    getRegionCoordinates(regionId, shortName) {
        // Approximate coordinates for UK regions
        const coordinates = {
            1: [58.0, -4.5],    // North Scotland
            2: [55.5, -3.5],    // South Scotland
            3: [54.0, -2.5],    // North West England
            4: [55.0, -1.5],    // North East England
            5: [54.0, -1.0],    // Yorkshire
            6: [53.0, -3.0],    // North Wales & Merseyside
            7: [51.5, -3.5],    // South Wales
            8: [52.5, -2.0],    // West Midlands
            9: [52.8, -1.0],    // East Midlands
            10: [52.5, 0.5],    // East England
            11: [50.5, -3.5],   // South West England
            12: [51.0, -1.0],   // South England
            13: [51.5, -0.1],   // London
            14: [51.2, 0.5],    // South East England
        };
        
        return coordinates[regionId] || [54.0, -2.0];
    }

    getIntensityColor(intensity) {
        if (intensity <= 50) return '#00ff00';      // Very Low
        if (intensity <= 100) return '#90ee90';    // Low
        if (intensity <= 200) return '#ffa500';    // Moderate
        if (intensity <= 300) return '#ff6b6b';    // High
        return '#dc143c';                          // Very High
    }

    getIntensityIndex(intensity) {
        if (intensity <= 50) return 'very low';
        if (intensity <= 100) return 'low';
        if (intensity <= 200) return 'moderate';
        if (intensity <= 300) return 'high';
        return 'very high';
    }

    updateMap() {
        if (!this.currentData || !this.currentData.regions) return;

        // Clear existing markers
        this.regionMarkers.forEach(marker => this.map.removeLayer(marker));
        this.regionMarkers = [];

        // Add markers for each region
        this.currentData.regions.forEach(region => {
            // Skip country-level aggregations (England, Scotland, Wales, GB)
            if (region.regionid > 14) return;

            const coords = this.getRegionCoordinates(region.regionid, region.shortname);
            const intensity = region.intensity.forecast;
            const color = this.getIntensityColor(intensity);

            const marker = L.circleMarker(coords, {
                radius: 15,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(this.map);

            // Popup content
            const popupContent = `
                <div class="popup-content">
                    <strong>${region.shortname}</strong><br>
                    <div class="popup-intensity" style="color: ${color}">
                        ${intensity} gCO₂/kWh
                    </div>
                    <em>${this.getIntensityIndex(intensity)}</em>
                </div>
            `;

            marker.bindPopup(popupContent);
            
            // Click event to show region details
            marker.on('click', () => {
                this.selectedRegion = region;
                this.updateRegionDetails();
                this.loadTimeSeries(region.regionid);
                // Update chart title
                document.getElementById('chart-title').textContent = `Time Series - ${region.shortname} (Last 24 Hours)`;
            });

            this.regionMarkers.push(marker);
        });
    }

    updateRegionDetails() {
        if (!this.selectedRegion) return;

        const region = this.selectedRegion;
        const regionName = document.getElementById('region-name');
        const regionDetails = document.getElementById('region-details');

        regionName.textContent = region.shortname;

        const intensity = region.intensity.forecast;
        const color = this.getIntensityColor(intensity);

        let detailsHTML = `
            <div class="intensity-value" style="color: ${color}">
                ${intensity} gCO₂/kWh
            </div>
            <p><strong>Index:</strong> ${this.getIntensityIndex(intensity)}</p>
            <p><strong>DNO Region:</strong> ${region.dnoregion}</p>
        `;

        if (region.generationmix) {
            detailsHTML += `
                <div class="generation-mix">
                    <h4>Generation Mix:</h4>
            `;
            
            region.generationmix
                .filter(fuel => fuel.perc > 0)
                .sort((a, b) => b.perc - a.perc)
                .forEach(fuel => {
                    detailsHTML += `
                        <div class="fuel-item">
                            <span>${fuel.fuel.charAt(0).toUpperCase() + fuel.fuel.slice(1)}:</span>
                            <span>${fuel.perc}%</span>
                        </div>
                    `;
                });
            
            detailsHTML += '</div>';
        }

        regionDetails.innerHTML = detailsHTML;
    }

    async loadTimeSeries(regionId) {
        try {
            // Get last 24 hours of data
            const endDate = new Date();
            const startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
            
            const from = startDate.toISOString().slice(0, -5) + 'Z';
            const to = endDate.toISOString().slice(0, -5) + 'Z';
            
            const response = await fetch(`https://api.carbonintensity.org.uk/regional/intensity/${from}/${to}/regionid/${regionId}`);
            const data = await response.json();
            
            console.log('Time series data:', data); // Debug log
            
            if (data.data && data.data.data && data.data.data.length > 0) {
                this.renderTimeSeries(data.data.data);
            } else {
                console.log('No time series data available');
                document.getElementById('time-series-chart').innerHTML = '<p>No time series data available for this region</p>';
            }
        } catch (error) {
            console.error('Error loading time series:', error);
            document.getElementById('time-series-chart').innerHTML = '<p>Error loading time series data</p>';
        }
    }

    renderTimeSeries(timeSeriesData) {
        const chartContainer = document.getElementById('time-series-chart');
        chartContainer.innerHTML = ''; // Clear previous chart

        if (!timeSeriesData || timeSeriesData.length === 0) {
            chartContainer.innerHTML = '<p>No time series data available</p>';
            return;
        }

        // Prepare data
        const data = timeSeriesData.map(d => ({
            time: new Date(d.from),
            intensity: d.intensity.forecast || 0
        })).sort((a, b) => a.time - b.time);

        // Set up dimensions
        const margin = { top: 20, right: 20, bottom: 40, left: 50 };
        const width = 280 - margin.left - margin.right;
        const height = 180 - margin.bottom - margin.top;

        // Create SVG
        const svg = d3.select('#time-series-chart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scaleTime()
            .domain(d3.extent(data, d => d.time))
            .range([0, width]);

        const yExtent = d3.extent(data, d => d.intensity);
        // Handle case where all values are the same
        const yScale = d3.scaleLinear()
            .domain(yExtent[0] === yExtent[1] ? [0, Math.max(yExtent[0] * 1.2, 10)] : yExtent)
            .nice()
            .range([height, 0]);

        // Line generator
        const line = d3.line()
            .x(d => xScale(d.time))
            .y(d => yScale(d.intensity))
            .curve(d3.curveMonotoneX);

        // Add axes
        g.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale)
                .tickFormat(d3.timeFormat('%H:%M')));

        g.append('g')
            .call(d3.axisLeft(yScale));

        // Add the line
        g.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', '#3498db')
            .attr('stroke-width', 2)
            .attr('d', line);

        // Add dots
        g.selectAll('.dot')
            .data(data)
            .enter().append('circle')
            .attr('class', 'dot')
            .attr('cx', d => xScale(d.time))
            .attr('cy', d => yScale(d.intensity))
            .attr('r', 3)
            .attr('fill', d => this.getIntensityColor(d.intensity));

        // Add axis labels
        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('y', 0 - margin.left)
            .attr('x', 0 - (height / 2))
            .attr('dy', '1em')
            .style('text-anchor', 'middle')
            .style('font-size', '12px')
            .text('Carbon Intensity (gCO₂/kWh)');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CarbonIntensityApp();
});