# AI for Coding Exercise: UK Carbon Intensity Visualization

## Overview

This exercise will help you practice using AI coding assistants to build a data 
visualization application. You'll create an interactive plot that displays 
carbon intensity data from the UK's national grid.

## Exercise Goal

Build a python application that interactively plots regional Carbon Intensity 
data onto a map of the UK. 
1. Fetches data from the UK Carbon Intensity API (https://carbonintensity.org.uk/)
2. Creates an interactive plot/visualization of the carbon intensity data 
   overlaid onto a map of the UK
3. Allows users to change the time being plotted, and plot a time-series for 
   a given region. 

## API Information

**Base URL:** `https://api.carbonintensity.org.uk/`

**Useful Endpoints:**
- Current intensity: `/intensity`
- Intensity for date range: `/intensity/{from}/{to}`
- Regional data: `/regional`
- Generation mix: `/generation`

**Documentation:** https://carbon-intensity.github.io/api-definitions/

## Getting Started

1. Choose your preferred programming framework:
   - Could use libraries like `requests`, `matplotlib`, `plotly`, or `streamlit`

2. Set up your development environment

3. Use your AI coding assistant to help you:
   - Understand the API structure
   - Write code to fetch data
   - Create visualizations
   - Debug issues
   - Add interactivity

## Example Features to Implement

- **Basic:** Display current carbon intensity
- **Intermediate:** Show intensity over time with a line chart
- **Advanced:** Compare regional differences, show generation mix, add forecasting

## Resources

- [UK Carbon Intensity API Documentation](https://carbon-intensity.github.io/api-definitions/)
- [Carbon Intensity Website](https://carbonintensity.org.uk/)


**Happy vibing**