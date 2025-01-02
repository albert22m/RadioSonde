import json

# Load the GeoJSON file
def load_geojson(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data