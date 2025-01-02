import matplotlib.pyplot as plt
import numpy as np
import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units
from matplotlib.gridspec import GridSpec
from get_city_name import get_city_name

def skewT_plot(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp, filename,
        pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
        pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el,
        pressure_ccl, temperature_ccl, height_ccl, pressures_cape, temperatures_cape, parcel_cape,
        pressures_cin, temperatures_cin,parcel_cin):
    # Create a new figure and Skew-T diagram
    fig = plt.figure(figsize=(10, 10), dpi=96)
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
    
    city = get_city_name(lat, lon)
    city = city.upper()

    # Add a title with aligned sections
    fig.suptitle('', x=0.5, y=0.97)  # Empty main title to avoid overlap
    skew.ax.set_title(f'Skew-T Log-P, {city}', loc='left', fontsize=14)
    skew.ax.set_title(timestamp, loc='center', fontsize=14)
    skew.ax.set_title(f'Lat = {lat:.2f}° Lon = {lon:.2f}°', loc='right', fontsize=14)

    # Add CAPE, CIN, LCL, LFC, EL, and CCL information
    fig.text(
        0.90, 0.93,
        r'$\bf{Instability\ Indices}$',
        fontsize=13,
        va='top',
        ha='center',
        linespacing=1.75
    )

    fig.text(
        0.85, 0.88,
        'CAPE\nCIN\nLCL\nLFC\nEL\nCCL',
        fontsize=12,
        va='top',
        ha='left',
        linespacing=1.75
    )

    text1 = (
        f'{cape.m:.2f} J/kg\n'
        f'{cin.m:.2f} J/kg\n'
        f'{height_lcl:.1f} m\n'
        f'{"N/A" if np.isnan(height_lfc) else f"{height_lfc:.1f} m"}\n'
        f'{"N/A" if np.isnan(height_el) else f"{height_el:.1f} m"}\n'
        f'{height_ccl:.1f} m'
    )

    fig.text(
        0.95, 0.88,
        text1,
        fontsize=12,
        va='top',
        ha='right',
        linespacing=1.75
    ) 

    fig.text(
        0.62, 0.50,
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

    #  Calculate above ground level (AGL) heights
    agl = (heights - heights[0]) / 1000
    mask = agl <= 10   # Limit to heights below 10 km
    intervals = np.array([0, 1, 3, 5, 8, 10])
    colors = ['tab:olive', 'tab:green', 'tab:blue', 'tab:red', 'tab:pink']

    # Add hodograph on the right
    gs = GridSpec(1, 2, left=0.5, bottom=0.5, right=0.8, top=1.13, wspace=0, hspace=0)
    ax_hodo = fig.add_subplot(gs[0, 1])
    h = Hodograph(ax_hodo, component_range=30.)
    h.add_grid(increment=10)
    l = h.plot_colormapped(
        wind_u[mask],
        wind_v[mask],
        agl[mask],
        intervals=intervals,
        colors=colors
    )
    # Add the colorbar with custom size
    cbar = plt.colorbar(l, ax=ax_hodo, orientation='vertical', pad=0.05, shrink=0.38)  # shrink value controls size
    cbar.set_label('Height (km)', fontsize=12)
    cbar.ax.tick_params(labelsize=10)

    ax_hodo.set_xlabel('Wind Speed (m/s)', fontsize=12)
    ax_hodo.set_ylabel('Wind Speed (m/s)', fontsize=12)

    # Save figure
    output_filename = filename.replace('.json', '.png')
    fig.set_size_inches(1920 / 96, 957 / 96)
    plt.savefig(output_filename, dpi = 96, format='png')

    # Show the plot
    plt.show()