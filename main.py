import os
import time
from datetime import timedelta
from load_geojson import load_geojson
from parse_geojson import parse_geojson
from skewT_calc import skewT_calc
from skewT_plot import skewT_plot

def main():
    filenames = [file for file in os.listdir('GeojsonData') if file.endswith('.json')]
    
    for filename in filenames:
        start_time = time.time()
        full_path = os.path.join('GeojsonData', filename)

        data = load_geojson(full_path)
        pressures, temperatures, dewpoints, wind_u, wind_v, heights, station_id, lat, lon, location, timestamp = parse_geojson(data)
        print_time = timestamp.strftime('%b %d, %Y at %M')
        print(f'  > PROFILE FOUND: {station_id} on {print_time}Z | {location}')

        (pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
         pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el, pressure_ccl, temperature_ccl, height_ccl,
         pressures_cape, temperatures_cape, parcel_cape, pressures_cin, temperatures_cin, parcel_cin, u_storm, v_storm,
         li, vt, tt, srh3, srh6, pwat, frz) = skewT_calc(
            pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat)
        
        skewT_plot(
            pressures, temperatures, dewpoints, wind_u, wind_v, heights, station_id, lat, lon, location, timestamp, filename,
            pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
            pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el,
            pressure_ccl, temperature_ccl, height_ccl, pressures_cape, temperatures_cape, parcel_cape, pressures_cin, temperatures_cin, parcel_cin,
            u_storm, v_storm, li, vt, tt, srh3, srh6, pwat, frz
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        formatted_time = str(timedelta(seconds=int(elapsed_time)))
        formatted_time = formatted_time.zfill(8)
        print(f'  > RUNTIME: {formatted_time}\n')

if __name__ == '__main__':
    main()
