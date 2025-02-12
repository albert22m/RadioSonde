# RadioSonde
This project processes meteorological sounding data in the GeoJSON format and generates Skew-T plots. It includes data extraction, calculations for pressure to geopotential height interpolation, and visualizations of atmospheric profiles.

## Repository Structure
The repository consists of the following directories and files:<br>
- **GeojsonData/**  
  Contains multiple .json files with meteorological sounding data.
  
- **Soundings/**  
  Contains .png files of the generated Skew-T plots.

- **get_city_name.py**  
  Extracts city names from GeoJSON data to identify the location of the sounding.

- **load_geojson.py**  
  Loads GeoJSON files.

- **parse_geojson.py**  
  Parses the loaded GeoJSON data and extracts necessary information.

- **calc.py**  
  Contains interpolation functions and other calculations.

- **skewT_calc.py**  
  Performs calculations to prepare the data for generating the Skew-T diagram.

- **skewT_plot.py**  
  Generates the Skew-T plot and saves the output.

- **main.py**  
  Main entry point for running the program.


To install and use this repository, make sure you have Python 3.x installed. Then, clone the repository and install the necessary dependencies using:<br>
```git clone <repository-url>```
```cd <repository-directory>```

To run the program, simply execute main.py:
```python main.py```
