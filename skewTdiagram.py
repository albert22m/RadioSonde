import json
import matplotlib.pyplot as plt
import numpy as np
from metpy.plots import SkewT
from metpy.units import units
from datetime import datetime, timedelta
from metpy.calc import cape_cin
from metpy.calc import parcel_profile

# Load the GeoJSON file
def load_geojson(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Parse the GeoJSON data for Skew-T plot
def parse_geojson(data):
    pressures = []  # in hPa
    temperatures = []  # in Celsius
    dewpoints = []  # in Celsius
    wind_u = []  # in m/s
    wind_v = []  # in m/s
    heights = []  # Geopotential height in meters
    timestamp = 0  # Unix timestamp

    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            props = feature['properties']
            pressures.append(props['pressure'])
            temperatures.append(props['temp'] - 273.15)  # Convert Kelvin to Celsius
            dewpoints.append(props['dewpoint'] - 273.15)  # Convert Kelvin to Celsius
            wind_u.append(props['wind_u'])
            wind_v.append(props['wind_v'])
            heights.append(props['gpheight'])  # Geopotential height

    # Extract latitude and longitude from the top-level properties
    lat = data['properties']['lat']
    lon = data['properties']['lon']

    # Unix timestamp
    timestamp = data['features'][0]['properties']['time']
    timestamp = datetime.utcfromtimestamp(timestamp)  # Convert the timestamp to a datetime object
    timestamp += timedelta(hours=1)
    timestamp = timestamp.strftime('%b %d, %Y %H:%M') + 'Z'  # Format the datetime as a human-readable string

    return (
        np.array(pressures),
        np.array(temperatures),
        np.array(dewpoints),
        np.array(wind_u),
        np.array(wind_v),
        np.array(heights),
        lat,
        lon,
        timestamp
    )

# Plot the Skew-T diagram
def plot_skewt(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp):
    # Filter data for pressures above 100 hPa
    valid_indices = pressures > 100  # Only include pressures above 100 hPa
    pressures = pressures[valid_indices]
    temperatures = temperatures[valid_indices]
    dewpoints = dewpoints[valid_indices]
    wind_u = wind_u[valid_indices]
    wind_v = wind_v[valid_indices]
    heights = heights[valid_indices]

    # Calculate CAPE and CIN using MetPy
    parcel_prof = parcel_profile(pressures * units.hPa, temperatures[0] * units.degC, dewpoints[0] * units.degC)
    cape, cin = cape_cin(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel_prof)

    # Create a new figure and Skew-T diagram
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45)

    # Plot the data
    skew.plot(pressures * units.hPa, temperatures * units.degC, 'r', label='Temperature')
    skew.plot(pressures * units.hPa, dewpoints * units.degC, 'b', label='Dew Point')
    skew.plot_barbs(pressures * units.hPa, wind_u * units.meter / units.second, wind_v * units.meter / units.second)
    skew.ax.axvline(0, color='brown', linestyle='-', linewidth=1, label='0°C Reference Line')

    # Add special lines with labels
    skew.plot_dry_adiabats(linewidth=0.8, colors='green', label='Dry Adiabats')
    skew.plot_moist_adiabats(linewidth=0.8, colors='darkorange', label='Moist Adiabats')
    skew.plot_mixing_lines(linewidth=0.8, colors='purple', label='Mixing Lines')

    # Add a legend outside the plot
    skew.ax.legend(
        loc='upper left',  # Anchor to the upper left of the axis
        fontsize=10,  # Font size
        frameon=True,  # Add a box around the legend
    )

    # Add a title with two aligned sections
    fig.suptitle('', x=0.5, y=0.97)  # Empty main title to avoid overlap
    skew.ax.set_title('Skew-T Log-P Diagram', loc='left', fontsize=14)
    skew.ax.set_title(timestamp, loc='center', fontsize=14)
    skew.ax.set_title(f'Lat = {lat:.2f}° Lon = {lon:.2f}°', loc='right', fontsize=14)

    # Add CAPE information
    fig.text(
        0.85, 0.85,  # horizontal, vertical
        f'CAPE = {cape.m / 1000:.2f} kJ/kg',
        fontsize=12,
        va='bottom',  # Vertical alignment
        ha='right'  # Horizontal alignment
    )

    # Labels and other adjustments
    plt.xlabel('Temperature (°C)', fontsize=12)
    plt.ylabel('Pressure (hPa)', fontsize=12)

    # Show the plot
    plt.show()


# Main execution
def main():
    filename = 'barcelona.json'
    data = load_geojson(filename)

    pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp = parse_geojson(data)

    plot_skewt(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp)

if __name__ == '__main__':
    main()
