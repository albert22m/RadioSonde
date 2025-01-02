import numpy as np
from metpy.units import units
from metpy.calc import cape_cin, parcel_profile, lfc, el, lcl, ccl
from pressure_to_height import pressure_to_height

# Plot the Skew-T diagram
def skewT_calc(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat, lon, timestamp, filename):
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
    height_lcl = pressure_to_height(pressure_lcl, pressures * units.hPa, heights)
    height_lfc = pressure_to_height(pressure_lfc, pressures * units.hPa, heights) if not np.isnan(pressure_lfc.magnitude) else np.nan
    height_el = pressure_to_height(pressure_el, pressures * units.hPa, heights) if not np.isnan(pressure_el.magnitude) else np.nan
    height_ccl = pressure_to_height(pressure_ccl, pressures * units.hPa, heights)

    # Limit the pressure range for CAPE and CIN shading
    cape_indices = (pressures <= pressure_lfc.magnitude) & (pressures >= pressure_el.magnitude)
    pressures_cape = pressures[cape_indices]
    temperatures_cape = temperatures[cape_indices]
    parcel_cape = parcel[cape_indices]

    cin_indices = pressures >= pressure_lfc.magnitude
    pressures_cin = pressures[cin_indices]
    temperatures_cin = temperatures[cin_indices]
    parcel_cin = parcel[cin_indices]

    return (
        np.array(pressures_short),
        np.array(wind_u_short),
        np.array(wind_v_short),
        np.array(parcel),
        cape,
        cin,
        np.array(pressure_lcl),
        np.array(temperature_lcl),
        np.array(height_lcl),
        np.array(pressure_lfc),
        np.array(temperature_lfc),
        np.array(height_lfc),
        np.array(pressure_el),
        np.array(temperature_el),
        np.array(height_el),
        np.array(pressure_ccl),
        np.array(temperature_ccl),
        np.array(height_ccl),
        pressures_cape,
        temperatures_cape,
        parcel_cape,
        pressures_cin,
        temperatures_cin,
        parcel_cin
    )