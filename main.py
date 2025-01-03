import os
from load_geojson import load_geojson
from parse_geojson import parse_geojson
from skewT_calc import skewT_calc
from skewT_plot import skewT_plot

def main():
    filenames = [file for file in os.listdir('GeojsonData') if file.endswith('.json')]
    
    for filename in filenames:
        full_path = os.path.join('GeojsonData', filename)
        print(f"Processing {filename}...")

        data = load_geojson(full_path)
        pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp = parse_geojson(data)
        
        (pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
         pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el, pressure_ccl, temperature_ccl, height_ccl,
         pressures_cape, temperatures_cape, parcel_cape, pressures_cin, temperatures_cin, parcel_cin) = skewT_calc(
            pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp, filename
        )
        
        skewT_plot(
            pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp, filename,
            pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
            pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el,
            pressure_ccl, temperature_ccl, height_ccl, pressures_cape, temperatures_cape, parcel_cape, pressures_cin, temperatures_cin, parcel_cin
        )

if __name__ == '__main__':
    main()
