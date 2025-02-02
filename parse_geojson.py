import numpy as np
from datetime import datetime
from get_city_name import get_city_name

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
            heights.append(props['gpheight'])

    # Extract latitude and longitude
    lat = data['properties']['lat']
    lon = data['properties']['lon']

    location = get_city_name(lat, lon)

    # Unix timestamp
    timestamp = data['properties']['syn_timestamp']
    timestamp = datetime.utcfromtimestamp(timestamp)  # Convert the timestamp to a datetime object

    # Station ID
    station_id = data['properties']['station_id']

    return (
        np.array(pressures),
        np.array(temperatures),
        np.array(dewpoints),
        np.array(wind_u),
        np.array(wind_v),
        np.array(heights),
        station_id,
        lat,
        lon,
        location,
        timestamp
    )