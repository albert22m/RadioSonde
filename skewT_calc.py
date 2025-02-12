import numpy as np
import metpy
from metpy.units import units
from metpy.calc import cape_cin, parcel_profile, lfc, el, lcl, ccl, lifted_index, vertical_totals, total_totals_index, storm_relative_helicity, precipitable_water
from calc import pressure_to_height

# Plot the Skew-T diagram
def skewT_calc(pressures, temperatures, dewpoints, wind_u, wind_v, heights, lat):
    # Filter data for pressures above 100 hPa
    valid_indices = pressures > 100
    pressures_short = pressures[valid_indices]
    wind_u_short = wind_u[valid_indices]
    wind_v_short = wind_v[valid_indices]
    heights_short = heights[valid_indices]

    # Calculate CAPE and CIN
    parcel = parcel_profile(pressures * units.hPa, temperatures[0] * units.degC, dewpoints[0] * units.degC)
    cape, cin = cape_cin(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel)

    # Calculate LCL, LFC, EL, and CCL
    pressure_lcl, temperature_lcl = lcl(pressures[0] * units.hPa, temperatures[0] * units.degC, dewpoints[0] * units.degC)
    pressure_lfc, temperature_lfc = lfc(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel, which='bottom')
    pressure_el, temperature_el = el(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC, parcel)
    pressure_ccl, temperature_ccl, _ = ccl(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC)

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

    # Bunkers storm motion (SFC-6km)
    bunkers_motion = metpy.calc.bunkers_storm_motion(pressures * units.hPa, wind_u * units.kts, wind_v * units.kts, heights * units.m)
    rm_storm, lm_storm, mean_wind = bunkers_motion

    if lat >= 0:
        u_storm = rm_storm[0].magnitude
        v_storm = rm_storm[1].magnitude
    else:
        u_storm = lm_storm[0].magnitude
        v_storm = lm_storm[1].magnitude

    # Lifting Index (LI), Vertical Totals Index (VT), Total Totals Index (TT)
    li = lifted_index(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC).magnitude[0]
    vt = vertical_totals(pressures * units.hPa, temperatures * units.degC).magnitude
    tt = total_totals_index(pressures * units.hPa, temperatures * units.degC, dewpoints * units.degC).magnitude

    # Storm Relative Winds
    u_storm_rel = wind_u_short - u_storm
    v_storm_rel = wind_v_short - v_storm

    # Compute Storm Relative Helicity (SRH)
    srh3 = storm_relative_helicity(heights * units.m, wind_u * units.kts, wind_v * units.kts,
        depth=3 * units.km, storm_u=u_storm * units.kts, storm_v=v_storm * units.kts)[0].magnitude
    srh6 = storm_relative_helicity(heights * units.m, wind_u * units.kts, wind_v * units.kts,
        depth=6 * units.km, storm_u=u_storm * units.kts, storm_v=v_storm * units.kts)[0].magnitude

    # Precipitable water
    pwat = precipitable_water(pressures * units.hPa, dewpoints * units.degC).magnitude

    # Freezing level
    frz = np.interp(0, temperatures[::-1], heights[::-1])

    return (
        pressures_short, wind_u_short, wind_v_short,
        parcel, cape, cin,
        pressure_lcl, temperature_lcl, height_lcl,
        pressure_lfc, temperature_lfc, height_lfc,
        pressure_el, temperature_el, height_el,
        pressure_ccl, temperature_ccl, height_ccl,
        pressures_cape, temperatures_cape, parcel_cape,
        pressures_cin, temperatures_cin, parcel_cin,
        u_storm, v_storm, li, vt, tt, srh3, srh6, pwat, frz
    )