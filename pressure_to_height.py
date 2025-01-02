from scipy.interpolate import interp1d
import numpy as np

def pressure_to_height(pressure_level, pressures, heights):
    """Interpolate height for a given pressure level using available data."""
    height_interp = interp1d(pressures, heights, bounds_error=False, fill_value=np.nan)
    return height_interp(pressure_level.m)