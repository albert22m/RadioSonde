import json

def load_geojson(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data