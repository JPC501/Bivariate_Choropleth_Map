# Bivariate Map of California: H.S. Diploma or Less vs. Unemployment Rate

This project generates a bivariate map of California counties, visualizing two key variables: Unemployment Rate and High School Diploma or Less. The map uses a bivariate color scale to display the relationship between these two variables for each county.

## Requirements

Before you begin, ensure you have the following:

- **Python** installed on your system.
- A development environment like **VS Code** or **PyCharm**.
- **Required data files**: 
  - A GeoJSON file containing the geographic boundaries of California counties.
  - A CSV file containing unemployment rate and high school diploma data for each county.

## Installation and Setup

### 1. Clone the Repository and Navigate to the Project Directory:
git clone <REPOSITORY_URL>  
cd <project_directory>

### 2. Create and Activate a Virtual Environment:

Create a virtual environment: 
```bash
python -m venv venv
```

Activate the virtual environment on Windows:
```bash   
venv\Scripts\activate
```  

Activate the virtual environment on macOS/Linux:
```bash  
source venv/bin/activate
```  

### 3. Install the Required Dependencies:

```bash
pip install -r requirements.txt
```

### 4. Required Files:
You will need two files for this project:

- A GeoJSON file: `California_County_Boundaries.geojson` (contains geographic data for California counties).
- A CSV file: `Cal-u-Rates-for-map.csv` (contains data for unemployment rate and high school diploma or less percentages).

Make sure both files are in the correct format before proceeding.

### 5. Edit File Paths:

In the script, update the file paths for the `California_County_Boundaries.geojson` and `Cal-u-Rates-for-map.csv` files to match your system's file structure:

```python
df_data = pd.read_csv("path/to/Cal-u-Rates-for-map.csv")  
geojson_path = "path/to/California_County_Boundaries.geojson"
```

## Running the Project

To run the project and generate the bivariate map:

1. **Activate the virtual environment** (if not already activated).
2. **Run the script**:

```python
python map.py
```

This will load the data, process the variables, and generate a map with county labels for California.

## CSV File Structure

Ensure that your CSV file has the following structure:

County,Unemployment-Rate,Rate H.S. Diploma or Less  
Alameda,5.1,49.4  
Alpine,7.7,64.5  
Amador,5.5,69.7

## GeoJSON File

Your GeoJSON file should contain the geographic boundaries of the counties in California. The county names in this file must match those in your CSV file for a successful merge.

## Example Output

The output is a bivariate choropleth map where:

- **X-Axis (Horizontal)**: Represents unemployment rates in percentage.
- **Y-Axis (Vertical)**: Represents the percentage of the population with a high school diploma or less.

Each county is colored according to the relationship between these two variables using a bivariate color scheme.
