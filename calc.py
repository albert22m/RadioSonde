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

def temp_advection(temperatures, wind_u, wind_v, heights):
    dTdz = np.gradient(temperatures, heights)
    dTdz = gaussian_filter1d(dTdz, sigma=1)
    temp_advection = - (wind_u * dTdz)
    return temp_advection