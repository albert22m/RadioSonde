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

def temp_advection(temperatures, pressures, wind_u, wind_v, heights, lat):
    """
    Compute temperature advection in °C/h.

    Parameters:
    - temperatures: Array of temperatures (K or °C)
    - pressures: Corresponding pressures (hPa or mb)
    - wind_u, wind_v: U/V components of wind (knots)
    - heights: Corresponding heights (m)
    - lat: Latitude for Coriolis effect

    Returns:
    - temp_adv: Temperature advection (°C/h)
    """

    wind_u = wind_u * 0.51444  # Convert to m/s
    wind_v = wind_v * 0.51444

    # Calculate temperature gradient (dT/dz or dT/dp)
    dTdp = np.gradient(temperatures, pressures)
    dTdz = -dTdp * (pressures / (287.05 * temperatures))  # Convert to dT/dz

    # Compute average temperature and mean wind for layers
    avg_temp = (temperatures[:-1] + temperatures[1:]) / 2
    mean_u = (wind_u[:-1] + wind_u[1:]) / 2
    mean_v = (wind_v[:-1] + wind_v[1:]) / 2
    wind_speed = np.sqrt(mean_u**2 + mean_v**2)

    # Calculate directional change (d_theta)
    wind_dir_bot = np.arctan2(wind_v[:-1], wind_u[:-1]) * (180 / np.pi)
    wind_dir_top = np.arctan2(wind_v[1:], wind_u[1:]) * (180 / np.pi)

    mod = 180 - wind_dir_bot
    wind_dir_top += mod
    wind_dir_top = np.where(wind_dir_top < 0, wind_dir_top + 360, wind_dir_top)
    wind_dir_top = np.where(wind_dir_top >= 360, wind_dir_top - 360, wind_dir_top)
    d_theta = wind_dir_top - 180

    # Coriolis parameter
    omega = 2 * np.pi / 86164
    f = abs(2 * omega * np.sin(np.radians(lat)))

    # Temperature advection
    temp_adv = -(f / 9.81) * wind_speed**2 * avg_temp * (d_theta / np.diff(heights)) * 3600  # °C/h

    return temp_adv