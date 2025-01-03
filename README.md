# RadioSonde
This project processes meteorological sounding data in the GeoJSON format and generates Skew-T plots. It includes data extraction, calculations for pressure to geopotential height interpolation, and visualizations of atmospheric profiles.

## Repository Structure
The repository consists of the following directories and files:<br>
`GeojsonData/`      - Contains multiple .json files with meteorological sounding data.<br>
`Soundings/`        - Contains .png files of the generated Skew-T plots.<br>
`get_city_name.py`  - Extracts city names from GeoJSON data to identify the location of the sounding.<br>
`load_geojson.py`   - Loads GeoJSON files.<br>
`parse_geojson.py`  - Parses the loaded GeoJSON data and extracts necessary information.<br>
`pressure_to_height.py` - Interpolates pressure to geopotential height using the data.<br>
`skewT_calc.py`     - Performs calculations to prepare the data for generating the Skew-T diagram.<br>
`skewT_plot.py`     - Generates the Skew-T plot and saves the output.<br>
`main.py`           - Main entry point for running the program.<br>

To install and use this repository, make sure you have Python 3.x installed. Then, clone the repository and install the necessary dependencies using:
```git clone <repository-url>```
```cd <repository-directory>```
```pip install -r requirements.txt```

To run the program, simply execute main.py:
```python main.py <geojson-file>```
