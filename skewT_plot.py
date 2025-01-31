import os
import math
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
        pressures_cin, temperatures_cin,parcel_cin, u_storm, v_storm, li, vt, tt, srh):
        
    # Create a new figure and Skew-T diagram
    fig = plt.figure(figsize=(10, 10), dpi=96)
    skew = SkewT(fig, rotation=45)
    
    skew.ax.yaxis.set_major_locator(plt.FixedLocator(np.arange(2, 11)*100))
    skew.ax.set_xlim(left=-39, right=49)

    skew.ax.tick_params(axis='x', which='major', direction='in', pad=-17, labelsize=15)
    skew.ax.tick_params(axis='y', which='major', direction='in', pad=-7, labelsize=15)
    for label in skew.ax.get_yticklabels():
        label.set_horizontalalignment('left')

    # Plot the data
    skew.ax.axvline(0, color='brown', linestyle='-', linewidth=1)
    skew.plot(pressures * units.hPa, temperatures * units.degC, 'r', label='Temperature')
    skew.plot(pressures * units.hPa, dewpoints * units.degC, 'b', label='Dew Point')
    skew.plot_barbs(pressures_short[::3] * units.hPa, wind_u_short[::3] * units.meter / units.second, wind_v_short[::3] * units.meter / units.second)
    
    # Add special lines with labels
    skew.plot_dry_adiabats(linewidth=1, colors='darkorange', label='Dry Adiabats')
    skew.plot_moist_adiabats(linewidth=1, colors='green', label='Moist Adiabats')
    skew.plot_mixing_lines(linewidth=1, colors='purple', label='Mixing Lines')

    # Shade the CAPE and CIN areas
    skew.shade_cape(pressures_cape * units.hPa, temperatures_cape * units.degC, parcel_cape)
    skew.shade_cin(pressures_cin * units.hPa, temperatures_cin * units.degC, parcel_cin)

    # Highlight LCL, LFC, EL, and CCL on the plot
    skew.ax.scatter(temperature_lcl, pressure_lcl, color='dodgerblue', zorder=10)
    skew.ax.annotate('LCL', xy=(temperature_lcl, pressure_lcl), xytext=(-10, -4),
                 textcoords='offset points', color='black', fontsize=12, ha='right',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_lfc, pressure_lfc, color='darkorange', zorder=10)
    skew.ax.annotate('LFC', xy=(temperature_lfc, pressure_lfc), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=12, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_el, pressure_el, color='chocolate', zorder=10)
    skew.ax.annotate('EL', xy=(temperature_el, pressure_el), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=12, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))
    skew.ax.scatter(temperature_ccl, pressure_ccl, color='limegreen', zorder=10)
    skew.ax.annotate('CCL', xy=(temperature_ccl, pressure_ccl), xytext=(10, -4),
                 textcoords='offset points', color='black', fontsize=12, ha='left',
                 bbox=dict(facecolor=(0.75, 0.75, 0.75, 0.5), edgecolor='grey', boxstyle='round,pad=0.2'))

    # Labels and other adjustments
    plt.xlabel('Temperature (°C)', fontsize=18)
    plt.ylabel('Pressure (hPa)', fontsize=18)

    secax = skew.ax.secondary_yaxis(1.03,
        functions=(
            lambda p: mpcalc.pressure_to_height_std(units.Quantity(p, 'hPa')).m_as('km'),
            lambda h: mpcalc.height_to_pressure_std(units.Quantity(h, 'km')).m
            )
        )
    secax.yaxis.set_major_locator(plt.FixedLocator(np.arange(0, 17)))
    secax.yaxis.set_minor_locator(plt.NullLocator())
    secax.yaxis.set_major_formatter(plt.ScalarFormatter())
    secax.tick_params(axis='y', which='major', labelsize=15)
    secax.set_ylabel('Height (km)', fontsize=18)
    
    # Add a legend outside the plot
    skew.ax.legend(
        loc='upper left',
        fontsize=15,
        frameon=True,
    )

    fig.subplots_adjust(left=-0.33, bottom=0.04, right=0.97, top=0.92, wspace=0, hspace=0)
    
    location = get_city_name(lat, lon)

    # Add a title with aligned sections
    fig.suptitle('', x=0.5, y=0.97)  # Empty main title to avoid overlap
    skew.ax.set_title(f'Skew-T Log-P, {location}', loc='left', fontsize=22)
    timestamp_plt = timestamp.strftime('%b %d, %Y %H:%M') + 'Z' # Format datetime object to string
    skew.ax.set_title(timestamp_plt, loc='center', fontsize=22)
    skew.ax.set_title(f'Lat = {lat:.2f}° Lon = {lon:.2f}°', loc='right', fontsize=22)

    #  Calculate above ground level (AGL) heights
    agl = (heights - heights[0]) / 1000
    mask = agl <= 10   # Limit to heights below 10 km
    intervals = np.array([0, 1, 3, 5, 8, 10])
    colors = ['tab:olive', 'tab:green', 'tab:blue', 'tab:red', 'tab:pink']

    component_range = max(abs(wind_u[mask].max()), abs(wind_u[mask].min()), abs(wind_v[mask].max()), abs(wind_v[mask].min()))
    component_range = math.ceil(component_range / 5) * 5
    valid_increments = np.array([5, 10, 15, 20])
    grid_increment = valid_increments[np.argmin(abs(valid_increments - component_range / 3))]
    
    # Add hodograph on the right
    gs = GridSpec(1, 2, left=0.35, bottom=0.4585, right=1, top=0.9385, wspace=0, hspace=0)
    ax_hodo = fig.add_subplot(gs[0, 1])
    h = Hodograph(ax_hodo, component_range=component_range)
    h.add_grid(increment=grid_increment)
    l = h.plot_colormapped(
        wind_u[mask],
        wind_v[mask],
        agl[mask],
        intervals=intervals,
        colors=colors
    )

    # Set limits with a margin of 0.1
    ax_hodo.set_xlim(-component_range + 0.1, component_range - 0.1)
    ax_hodo.set_ylim(-component_range + 0.1, component_range - 0.1)

    # Add storm motion vector to the hodograph
    ax_hodo.quiver(
        0, 0,  # Start at origin
        u_storm, v_storm,  # Storm motion vector
        angles='xy', scale_units='xy', scale=1, color='grey', width=0.01
    )
    ax_hodo.tick_params(axis='x', which='major', direction='in', pad=-17, labelsize=15)
    ax_hodo.tick_params(axis='y', which='major', direction='in', pad=-5, labelsize=15)
    for label in ax_hodo.get_yticklabels():
        label.set_horizontalalignment('left')

    # Add the colorbar with custom size
    cbar = plt.colorbar(l, ax=ax_hodo, orientation='vertical', pad=0, shrink=0.922, aspect=40)  # shrink (size), aspect(thickness)
    cbar.set_label('Height (km)', fontsize=18)
    cbar.ax.tick_params(labelsize=15)

    ax_hodo.text(
    0.5, 1.022,  # Position: horizontal, vertical
    'Wind Speed (m/s)',
    fontsize=18,
    rotation=0,
    ha='center', va='center',
    transform=ax_hodo.transAxes  # Use axis coordinates
    )

    fig.text(
        0.025, 0.98,
        r'$\bf{RAOB\ OBSERVED\ VERTICAL\ PROFILE}$',
        fontsize=30,
        va='top',
        ha='left'
    )

    # Add numerical information
    fig.text(
        0.74, 0.43,  # Position (X, Y) for table title
        r'$\bf{Instability\ Indices}$',
        fontsize=18,
        va='top',
        ha='center',
        linespacing=1.75
    )

    # Define the table rows (left column: indices, center column: values, right column: units)
    table_labels = [
        'CAPE',
        'CIN',
        'LI',
        'VT',
        'TT',
        'SRH-3 km'
    ]
    table_values = [
        f'{cape.m:.2f}',
        f'{cin.m:.2f}',
        f'{li:.0f}',
        f'{vt:.0f}',
        f'{tt:.0f}',
        f'{srh:.0f}'
    ]
    table_units = [
        'J/kg',
        'J/kg',
        'Δ°C',
        'Δ°C',
        'Δ°C',
        'm²/s²'
    ]

    # Set the table position (starting X, Y coordinates)
    table_x_left = 0.685  # X position for labels
    table_x_center = table_x_left + 0.08  # X position for values
    table_x_right = table_x_center + 0.01  # X position for units
    table_y_start = 0.38  # Starting Y position
    line_spacing = 0.035  # Vertical spacing between rows

    # Render the table rows
    for i, (label, value, unit) in enumerate(zip(table_labels, table_values, table_units)):
        fig.text(
            table_x_left, table_y_start - i * line_spacing,  # Position for labels
            label,
            fontsize=18,
            va='top',
            ha='left'
        )
        fig.text(
            table_x_center, table_y_start - i * line_spacing,  # Position for values
            value,
            fontsize=18,
            va='top',
            ha='right'
        )
        fig.text(
            table_x_right, table_y_start - i * line_spacing,  # Position for units
            unit,
            fontsize=18,
            va='top',
            ha='left'
        )

    fig.text(
        0.89, 0.43,  # Position (X, Y) for table title
        r'$\bf{Profile\ Parameters}$',
        fontsize=18,
        va='top',
        ha='center',
        linespacing=1.75
    )

    table_labels = [
        'PWAT',
        'LCL',
        'LFC',
        'EL',
        'CCL'
    ]
    table_values = [
        'N/A',
        f'{height_lcl:.1f}',
        'N/A' if np.isnan(height_lfc) else f'{height_lfc:.1f}',
        'N/A' if np.isnan(height_el) else f'{height_el:.1f}',
        f'{height_ccl:.1f}'
    ]
    table_units = [
        'mm',
        'm',
        'm',
        'm',
        'm'
    ]

    # Set the table position (starting X, Y coordinates)
    table_x_left = 0.835  # X position for labels
    table_x_center = table_x_left + 0.08  # X position for values
    table_x_right = table_x_center + 0.01  # X position for units
    table_y_start = 0.38  # Starting Y position
    line_spacing = 0.035  # Vertical spacing between rows

    # Render the table rows
    for i, (label, value, unit) in enumerate(zip(table_labels, table_values, table_units)):
        fig.text(
            table_x_left, table_y_start - i * line_spacing,  # Position for labels
            label,
            fontsize=18,
            va='top',
            ha='left'
        )
        fig.text(
            table_x_center, table_y_start - i * line_spacing,  # Position for values
            value,
            fontsize=18,
            va='top',
            ha='right'
        )
        fig.text(
            table_x_right, table_y_start - i * line_spacing,  # Position for units
            unit,
            fontsize=18,
            va='top',
            ha='left'
        )

    # Save figure
    output_dir = "Soundings"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the plot in the 'Soundings' directory
    output_filename = filename.replace('.json', '')
    timestamp_fig = timestamp.strftime('%Y%m%d%H')
    output_filename = os.path.join(output_dir, f"{output_filename}_{timestamp_fig}.png")
    
    fig.set_size_inches(2455 / 96,1532 / 96)
    plt.savefig(output_filename, dpi = 96, format='png')

    #plt.show(block=False)
    #plt.pause(.1)
    #plt.close()