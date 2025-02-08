import os
import math
import matplotlib.pyplot as plt
import numpy as np
import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units
from matplotlib.gridspec import GridSpec
import geopandas as gpd
from matplotlib.patches import Circle
from calc import height_to_pressure, temp_advection

def skewT_plot(pressures, temperatures, dewpoints, wind_u, wind_v, heights, elevation, station_id, lat, lon, location, timestamp, filename,
        pressures_short, wind_u_short, wind_v_short, parcel, cape, cin, pressure_lcl, temperature_lcl, height_lcl,
        pressure_lfc, temperature_lfc, height_lfc, pressure_el, temperature_el, height_el,
        pressure_ccl, temperature_ccl, height_ccl, pressures_cape, temperatures_cape, parcel_cape,
        pressures_cin, temperatures_cin,parcel_cin, u_storm, v_storm, li, vt, tt, srh3, srh6, pwat, frz):
        
    # Create a new figure and Skew-T diagram
    fig = plt.figure(figsize=(10, 10), dpi=96)
    skew = SkewT(fig, rotation=45)
    
    skew.ax.yaxis.set_major_locator(plt.FixedLocator(np.arange(2, 11)*100))
    skew.ax.set_xlim(left=-39, right=49)

    skew.ax.tick_params(axis='x', which='major', direction='in', pad=-17, labelsize=15)
    skew.ax.tick_params(axis='y', which='major', direction='in', pad=-7, labelsize=15)
    for label in skew.ax.get_xticklabels():
        label.set_fontweight('bold')
    for label in skew.ax.get_yticklabels():
        label.set_fontweight('bold')
        label.set_horizontalalignment('left')

    # Plot the data
    skew.ax.axvline(0, color='brown', linestyle='-', linewidth=1)
    skew.plot(pressures * units.hPa, temperatures * units.degC, 'r', label='Temperature')
    skew.plot(pressures * units.hPa, dewpoints * units.degC, 'b', label='Dew Point')
    skew.plot_barbs(pressures_short[::3] * units.hPa, wind_u_short[::3] * units.meter / units.second,
        wind_v_short[::3] * units.meter / units.second, xloc=0.97)
    trans, _, _ = skew.ax.get_yaxis_text1_transform(0)  # Transformation for the y-axis text alignment
    plt.plot([0.97, 0.97], [100, 1050], 
         color='black', linestyle='-', linewidth=0.8, transform=trans)
    
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

    # Add height axis
    for height in [1000, 3000, 5000, 7000, 9000, 13000]:
        pressure = height_to_pressure(height, heights, pressures)
        skew.ax.text(
            0.05, pressure,
            f"{int(height / 1000)}km",
            fontsize=15,
            transform=trans,
            alpha=0.85,
            weight='bold',
            color='grey'
        )

    skew.ax.text(
            0.05, height_to_pressure(elevation, heights, pressures),
            f"SFC ({int(elevation)}m)",
            fontsize=15,
            transform=trans,
            alpha=0.85,
            weight='bold',
            color='grey'
        )

    fig.subplots_adjust(left=-0.33, bottom=0.04, right=0.97, top=0.92, wspace=0, hspace=0)

    # Add a title with aligned sections
    fig.suptitle('', x=0.5, y=0.97)  # Empty main title to avoid overlap
    skew.ax.set_title(f'Skew-T Log-P, {location}', loc='left', fontsize=22)
    timestamp_plt = timestamp.strftime('%b %d, %Y %H:%M') + 'Z' # Format datetime object to string
    skew.ax.set_title(timestamp_plt, loc='center', fontsize=22)
    skew.ax.set_title(f'{station_id} | {lat:.2f}°, {lon:.2f}°', loc='right', fontsize=22)

    # Temperature advection ---------------------------------------------------------------------------------------------------
    # Define pressure layers (boundaries)
    layer_bounds = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]

    # Compute temperature advection values
    temp_adv = temp_advection(temperatures, pressures, wind_u, wind_v, heights, lat)

    # Aggregate temperature advection values for each pressure layer
    layer_temp_adv = []  # Averaged temperature advection for each layer
    for i in range(len(layer_bounds) - 1):
        # Find indices of pressures within the current layer
        layer_mask = (pressures[:-1] >= layer_bounds[i + 1]) & (pressures[:-1] < layer_bounds[i])
        
        # Compute the mean temperature advection for this layer
        if np.any(layer_mask):  # Ensure there are values in this layer
            mean_adv = np.mean(temp_adv[layer_mask])
            layer_temp_adv.append(mean_adv)
        else:
            layer_temp_adv.append(np.nan)  # No data in this layer

    # Prepare top and bottom bounds for each bar
    bot_arr = layer_bounds[:-1]  # Bottom of each layer
    top_arr = layer_bounds[1:]   # Top of each layer

    # Add temp_adv plot to the right
    temp_adv_ax = fig.add_axes((0.614, 0.04, 0.061, 0.88))  # Adjust position and size (x, y, width, height)

    # Set plot styles
    temp_adv_ax.spines["top"].set_color('black')
    temp_adv_ax.spines["left"].set_color('black')
    temp_adv_ax.spines["right"].set_color('black')
    temp_adv_ax.spines["bottom"].set_color('black')

    # Set axis limits and scaling
    temp_adv_ax.set_yscale('log')
    temp_adv_ax.set_ylim(1050, 100)
    temp_adv_ax.set_xlim(-np.nanmax(np.abs(layer_temp_adv)) - 4, np.nanmax(np.abs(layer_temp_adv)) + 4)
    temp_adv_ax.set_yticklabels([]), temp_adv_ax.set_xticklabels([])
    temp_adv_ax.tick_params(axis='y', length=0), temp_adv_ax.tick_params(axis='x', length=0)

    # Draw horizontal reference lines
    lvls = [1000, 900, 800, 700, 600, 500, 400, 300, 200]
    for lvl in lvls:
        temp_adv_ax.plot((-np.nanmax(np.abs(layer_temp_adv)) - 4, np.nanmax(np.abs(layer_temp_adv)) + 4),
            (lvl, lvl), color='gray', alpha=0.8, linewidth=1, linestyle='-', clip_on=True)

    # Plot temperature advection bars
    for i in range(len(layer_temp_adv)):
        if not np.isnan(layer_temp_adv[i]):  # Skip layers with no data
            color = 'red' if layer_temp_adv[i] > 0 else 'cornflowerblue'
            
            temp_adv_ax.barh(
                (top_arr[i] + bot_arr[i]) / 2,  # Center of the bar
                layer_temp_adv[i],  # Advection value
                align='center',
                height=bot_arr[i] - top_arr[i],  # Height of the bar
                edgecolor='black',
                alpha=0.3,
                color=color
            )

            # Add annotations for temperature advection values
            if abs(layer_temp_adv[i]) > 0.1:  # Threshold to avoid clutter
                ha = 'left' if layer_temp_adv[i] > 0 else 'right'
                x_offset = 0.3 if layer_temp_adv[i] > 0 else -0.3
                temp_adv_ax.annotate(
                    f"{layer_temp_adv[i]:.1f}", 
                    xy=(x_offset, (top_arr[i] + bot_arr[i]) / 2),  # Center of the bar
                    color='black',
                    textcoords='data', ha=ha, weight='bold'
                )

    # Add a vertical reference line at x=0
    temp_adv_ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--', clip_on=True)
    temp_adv_ax.set_xlabel('°C/h', fontsize=18)

    #  Calculate above ground level (AGL) heights -----------------------------------------------------------------------------
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

    # Turn off default axis ticks
    ax_hodo.set_xticks([])
    ax_hodo.set_yticks([])

    # Add storm motion vector to the hodograph
    ax_hodo.quiver(
        0, 0,  # Start at origin
        u_storm, v_storm,  # Storm motion vector
        angles='xy', scale_units='xy', scale=1, color='grey', width=0.01
    )
    ax_hodo.annotate('RM' if lat >= 0 else 'LM', xy=(u_storm, v_storm), xytext=(5, 0), weight='bold',
                 textcoords='offset points', color='grey', fontsize=15, ha='left', va='center')

    ax_hodo.tick_params(axis='x', which='major', direction='in', pad=-17, labelsize=15)
    ax_hodo.tick_params(axis='y', which='major', direction='in', pad=-5, labelsize=15)
    for label in ax_hodo.get_yticklabels():
        label.set_horizontalalignment('left')

    velocity_range = np.arange(0, component_range + 1, grid_increment)
    for vel in velocity_range[1:]:  # Skip 0 to avoid overlapping at the center
        # Positive X-axis
        ax_hodo.annotate(
            str(vel), (vel, 0), xytext=(0, -15), textcoords='offset points',
            ha='center', va='center', fontsize=15, color='black'
        )
        # Negative X-axis
        ax_hodo.annotate(
            str(vel), (-vel, 0), xytext=(0, -15), textcoords='offset points',
            ha='center', va='center', fontsize=15, color='black'
        )
        # Positive Y-axis
        ax_hodo.annotate(
            str(vel), (0, vel), xytext=(-15, 0), textcoords='offset points',
            ha='center', va='center', fontsize=15, color='black'
        )
        # Negative Y-axis
        ax_hodo.annotate(
            str(vel), (0, -vel), xytext=(-15, 0), textcoords='offset points',
            ha='center', va='center', fontsize=15, color='black'
        )

    # Add the colorbar with custom size
    cbar = plt.colorbar(l, ax=ax_hodo, orientation='vertical', pad=0, shrink=0.922, aspect=40)  # shrink (size), aspect(thickness)
    cbar.set_label('Height (km)', fontsize=18)
    cbar.ax.tick_params(labelsize=15)

    # Cartographic map --------------------------------------------------------------------------------------------------------
    # Parameters: left, bottom, width, height
    ax_map = fig.add_axes([0.4515, 0.72, 0.2, 0.2])

    admin1 = gpd.read_file("https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip")
    admin2 = gpd.read_file("https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_2_counties.zip")

    admin1.boundary.plot(ax=ax_map, linewidth=1, color='black', alpha=1)
    admin2.boundary.plot(ax=ax_map, linewidth=0.5, color='black', alpha=0.5)

    ax_map.set_aspect('equal', adjustable='box')

    # Automatically zoom to the specific point with a buffer around i
    buffer = 2  # Buffer size (controls the zoom level)
    ax_map.set_xlim(lon - buffer, lon + buffer)
    ax_map.set_ylim(lat - buffer, lat + buffer)

    # Draw marker
    circle = Circle((lon, lat), radius=0.075, color='black', fill=False, linewidth=1)
    ax_map.add_patch(circle)
    ax_map.plot([lon - 0.1, lon + 0.1], [lat, lat], color='black', linewidth=1)  # Horizontal line
    ax_map.plot([lon, lon], [lat - 0.1, lat + 0.1], color='black', linewidth=1)  # Vertical line

    # Remove axis ticks and labels for the map
    ax_map.set_xticks([])
    ax_map.set_yticks([])
    ax_map.set_xticklabels([])
    ax_map.set_yticklabels([])

    # Add text ----------------------------------------------------------------------------------------------------------------
    fig.lines.append(plt.Line2D([0.675, 0.675], [0.45, 0.04],
                            transform=fig.transFigure, color='black', linewidth=0.8))
    fig.lines.append(plt.Line2D([0.97, 0.97], [0.45, 0.04],
                            transform=fig.transFigure, color='black', linewidth=0.8))
    fig.lines.append(plt.Line2D([0.97, 0.675], [0.04, 0.04],
                            transform=fig.transFigure, color='black', linewidth=0.8))
    fig.lines.append(plt.Line2D([0.97, 0.675], [0.45, 0.45],
                            transform=fig.transFigure, color='black', linewidth=0.8))
        
    ax_hodo.text(
    0.5, 1.022,  # Position: horizontal, vertical
    'Wind Speed (kts)',
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
        'SRH-3 km',
        'SRH-6 km'
    ]
    table_values = [
        f'{cape.m:.1f}',
        f'{cin.m:.1f}',
        f'{li:.0f}',
        f'{vt:.0f}',
        f'{tt:.0f}',
        f'{srh3:.0f}',
        f'{srh6:.0f}'
    ]
    table_units = [
        'J/kg',
        'J/kg',
        'Δ°C',
        'Δ°C',
        'Δ°C',
        'm²/s²',
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
        0.90, 0.43,  # Position (X, Y) for table title
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
        'CCL',
        'FRZ'
    ]
    table_values = [
        f'{pwat:.0f}',
        f'{height_lcl:.0f}',
        'N/A' if np.isnan(height_lfc) else f'{height_lfc:.0f}',
        'N/A' if np.isnan(height_el) else f'{height_el:.0f}',
        f'{height_ccl:.0f}',
        f'{frz:.0f}'
    ]
    table_units = [
        'mm',
        'm',
        'm',
        'm',
        'm',
        'm'
    ]

    # Set the table position (starting X, Y coordinates)
    table_x_left = 0.845  # X position for labels
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