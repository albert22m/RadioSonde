import json
import matplotlib.pyplot as plt
import numpy as np
import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units
from datetime import datetime, timedelta
from metpy.calc import cape_cin, parcel_profile, lfc, el, lcl, ccl
from scipy.interpolate import interp1d

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

def interpolate_height(pressure_level, pressures, heights):
    """Interpolate height for a given pressure level using available data."""
    height_interp = interp1d(pressures, heights, bounds_error=False, fill_value=np.nan)
    return height_interp(pressure_level.m)

# Plot the Skew-T diagram
def plot_skewt(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp):
    # Filter data for pressures above 100 hPa
    valid_indices = pressures > 100
    pressures_short = pressures[valid_indices]
    wind_u_short = wind_u[valid_indices]
    wind_v_short = wind_v[valid_indices]

    # Calculate CAPE and CIN
    parcel = parcel_profile(pressures * units.hPa, temperatures[0] * units.degC, dewpoints[0] * units.degC)
    cape, cin = cape_cin(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel)

    # Calculate LCL, LFC, EL, and CCL
    pressure_lcl, temperature_lcl = lcl(pressures[0] * units.hPa, temperatures[0] * units.degC, dewpoints[0] * units.degC)
    pressure_lfc, temperature_lfc = lfc(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel)
    pressure_el, temperature_el = el(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel)
    pressure_ccl, temperature_ccl, _ = ccl(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC)

    # Ensure LFC and EL pressures have the same units as the profile pressures
    pressure_lfc = pressure_lfc.to(units.hPa)
    pressure_el = pressure_el.to(units.hPa)

    # Interpolate heights from the geopotential height data
    height_lcl = interpolate_height(pressure_lcl, pressures * units.hPa, heights)
    height_lfc = interpolate_height(pressure_lfc, pressures * units.hPa, heights) if not np.isnan(pressure_lfc.magnitude) else np.nan
    height_el = interpolate_height(pressure_el, pressures * units.hPa, heights) if not np.isnan(pressure_el.magnitude) else np.nan
    height_ccl = interpolate_height(pressure_ccl, pressures * units.hPa, heights)

    # Limit the pressure range for CAPE and CIN shading
    cape_indices = (pressures <= pressure_lfc.magnitude) & (pressures >= pressure_el.magnitude)
    pressures_cape = pressures[cape_indices]
    temperatures_cape = temperatures[cape_indices]
    parcel_cape = parcel[cape_indices]

    cin_indices = pressures >= pressure_lfc.magnitude
    pressures_cin = pressures[cin_indices]
    temperatures_cin = temperatures[cin_indices]
    parcel_cin = parcel[cin_indices]

    # Create a new figure and Skew-T diagram
    fig = plt.figure(figsize=(10, 10))
    skew = SkewT(fig, rotation=45)

    # Plot the data
    skew.plot(pressures * units.hPa, temperatures * units.degC, 'r', label='Temperature')
    skew.plot(pressures * units.hPa, dewpoints * units.degC, 'b', label='Dew Point')
    skew.plot_barbs(pressures_short[::3] * units.hPa, wind_u_short[::3] * units.meter / units.second, wind_v_short[::3] * units.meter / units.second)
    skew.ax.axvline(0, color='brown', linestyle='-', linewidth=1, label='0°C Reference Line')

    # Add special lines with labels
    skew.plot_dry_adiabats(linewidth=1, colors='darkorange', label='Dry Adiabats')
    skew.plot_moist_adiabats(linewidth=1, colors='green', label='Moist Adiabats')
    skew.plot_mixing_lines(linewidth=1, colors='purple', label='Mixing Lines')

    # Shade the CAPE and CIN areas
    skew.shade_cape(pressures_cape * units.hPa, temperatures_cape * units.degC, parcel_cape)
    skew.shade_cin(pressures_cin * units.hPa, temperatures_cin * units.degC, parcel_cin)
    
    # Highlight LCL, LFC, EL, and CCL on the plot
    skew.ax.scatter(temperature_lcl, pressure_lcl, color='magenta', zorder=10)
    skew.ax.annotate('LCL', xy=(temperature_lcl, pressure_lcl), xytext=(-10, -4),
                 textcoords='offset points', color='black', fontsize=9, ha='right',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_lfc, pressure_lfc, color='lime', zorder=10)
    skew.ax.annotate('LFC', xy=(temperature_lfc, pressure_lfc), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=9, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_el, pressure_el, color='cyan', zorder=10)
    skew.ax.annotate('EL', xy=(temperature_el, pressure_el), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=9, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_ccl, pressure_ccl, color='orange', zorder=10)
    skew.ax.annotate('CCL', xy=(temperature_ccl, pressure_ccl), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=9, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))

    secax = skew.ax.secondary_yaxis(1.07,
        functions=(
            lambda p: mpcalc.pressure_to_height_std(units.Quantity(p, 'hPa')).m_as('km'),
            lambda h: mpcalc.height_to_pressure_std(units.Quantity(h, 'km')).m
            )
        )
    secax.yaxis.set_major_locator(plt.FixedLocator([0, 1, 3, 6, 9, 12, 15]))
    secax.yaxis.set_minor_locator(plt.NullLocator())
    secax.yaxis.set_major_formatter(plt.ScalarFormatter())
    secax.set_ylabel('Height (km)')
    
    # Add a legend outside the plot
    skew.ax.legend(
        loc='upper left',
        fontsize=10,
        frameon=True,
    )

    # Add a title with two aligned sections
    fig.suptitle('', x=0.5, y=0.97)  # Empty main title to avoid overlap
    skew.ax.set_title('Skew-T Log-P Diagram', loc='left', fontsize=14)
    skew.ax.set_title(timestamp, loc='center', fontsize=14)
    skew.ax.set_title(f'Lat = {lat:.2f}° Lon = {lon:.2f}°', loc='right', fontsize=14)

    # Add CAPE, CIN, LCL, LFC, EL, and CCL information
    fig.text(
        0.75, 0.85,
        'CAPE\n'
        'CIN\n'
        'LCL\n'
        'LFC\n'
        'EL\n'
        'CCL',
        fontsize=12,
        va='top',
        ha='left'
    )

    fig.text(
        0.85, 0.85,
        f'{cape.m:.2f} J/kg\n'
        f'{cin.m:.2f} J/kg\n'
        f'{height_lcl:.1f} m\n'
        f'{"N/A" if np.isnan(height_lfc) else f"{height_lfc:.1f} m"}\n'
        f'{"N/A" if np.isnan(height_el) else f"{height_el:.1f} m"}\n'
        f'{height_ccl:.1f} m',
        fontsize=12,
        va='top',
        ha='right'
    )

    fig.text(
        0.62, 0.55,
        r'$\bf{Convective\ Available\ Potential\ Energy\ (CAPE):\ }$'
        'is a measure of the amount of\nenergy available for convection in the atmosphere. It indicates the potential for\n'
        'thunderstorms and severe weather by quantifying the buoyancy of air parcels.\n\n'
        r'$\bf{Convective\ Inhibition\ (CIN):\ }$'
        'refers to the energy that prevents air parcels from\nrising and developing convection. It represents a layer of the'
        ' atmosphere where the\ntemperature increases with height, inhibiting the upward motion of air.\n\n'
        r'$\bf{Lifted\ Condensation\ Level\ (LCL):\ }$'
        'is the height where unsaturated air from the\nsurface will cool and reach saturation. This makes it the level'
        ' of the cloud base\nwhen fronts move on.\n\n'
        r'$\bf{Level\ of\ Free\ Convection\ (LFC):\ }$'
        'is the altitude at which a lifted air parcel\nbecomes buoyant enough to continue rising freely and accelerate upward,'
        '\nforming a thunderstorm.\n\n'
        r'$\bf{Equilibrium\ Level\ (EL):\ }$'
        'is the altitude at which a rising air parcel becomes cooler\nthan the surrounding air and stops rising. The EL is'
        ' often associated with the top of\na thunderstorm cloud.\n\n'
        r'$\bf{Convective\ Condensation\ Level\ (CCL):\ }$'
        'is the height at which air from the\nsurface will become saturated when lifted convectively.\n\n'
        ,
        fontsize=12,
        va='top',
        ha='left'
    )

    # Labels and other adjustments
    plt.xlabel('Temperature (°C)', fontsize=12)
    plt.ylabel('Pressure (hPa)', fontsize=12)

    fig.subplots_adjust(left=-0.4, bottom=0.07, right=1, top=0.95, wspace=0, hspace=0)

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
