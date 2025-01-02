import numpy as np
from datetime import datetime, timedelta

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

    # Extract latitude and longitude
    lat = data['properties']['lat']
    lon = data['properties']['lon']

    # Unix timestamp
    timestamp = data['features'][0]['properties']['time']
    timestamp = datetime.utcfromtimestamp(timestamp)  # Convert the timestamp to a datetime object
    timestamp += timedelta(hours=1)
    timestamp = timestamp.strftime('%b %d, %Y %H:%M') + 'Z'  # Format the datetime as string

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