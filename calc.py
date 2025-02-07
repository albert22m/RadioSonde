from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def pressure_to_height(pressure_level, pressures, heights):
    """Interpolate height for a given pressure level using available data."""
    height_interp = interp1d(pressures, heights, bounds_error=False, fill_value=np.nan)
    return height_interp(pressure_level.m)

def height_to_pressure(height_level, heights, pressures):
    """Interpolate pressure for a given height level using available data."""
    pressure_interp = interp1d(heights[::-1], pressures[::-1], bounds_error=False, fill_value=np.nan)
    return pressure_interp(height_level)

def temp_advection(temperatures, wind_u, wind_v, heights, lat):
    """
    Compute temperature advection in °C/s considering both horizontal wind components.

    Parameters:
    - temperatures: Array of temperatures (K or °C)
    - wind_u: U-component of wind (knots) → will be converted to m/s
    - wind_v: V-component of wind (knots) → will be converted to m/s
    - heights: Corresponding heights (m)
    - lat: Latitude for Coriolis effect

    Returns:
    - temp_adv: Temperature advection (°C/h)
    """

    wind_u = wind_u * 0.51444
    wind_v = wind_v * 0.51444

    # Compute temperature gradient (dT/dz)
    dTdz = np.gradient(temperatures, heights)
    print(dTdz[:4])

    # Compute wind speed and direction
    wind_speed = np.sqrt(wind_u**2 + wind_v**2)  # Wind magnitude (m/s)
    wind_dir = np.arctan2(wind_v, wind_u) * (180 / np.pi)  # Convert to degrees
    print(wind_speed[:4])
    print(wind_dir[:4])

    # Compute Coriolis parameter f (s⁻¹)
    omega = 2 * np.pi / 86164  # Earth's rotation rate (rad/s)
    f = 2 * omega * np.sin(np.radians(lat))  # Coriolis parameter

    # Compute advection: -Vg * (dT/dz) (SHARPpy-style)
    temp_adv = - (f / 9.81) * wind_speed**2 * dTdz * 3600
    print(temp_adv[:4])

    return temp_adv