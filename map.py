import json
import math
import os
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import requests


def conf_defaults():
    # Define some variables for later use
    conf = {
        "plot_title": "Bivariate choropleth map using Ploty",  # Title text
        "plot_title_size": 20,  # Font size of the title
        "width": 1000,  # Width of the final map container
        "ratio": 0.8,  # Ratio of height to width
        "center_lat": 0,  # Latitude of the center of the map
        "center_lon": 0,  # Longitude of the center of the map
        "map_zoom": 3,  # Zoom factor of the map
        "hover_x_label": "Label x variable",  # Label to appear on hover
        "hover_y_label": "Label y variable",  # Label to appear on hover
        "borders_width": 0.5,  # Width of the geographic entity borders
        "borders_color": "#f8f8f8",  # Color of the geographic entity borders
        # Define settings for the legend
        "top": 1,  # Vertical position of the top right corner (0: bottom, 1: top)
        "right": 1,  # Horizontal position of the top right corner (0: left, 1: right)
        "box_w": 0.04,  # Width of each rectangle
        "box_h": 0.04,  # Height of each rectangle
        "line_color": "#f8f8f8",  # Color of the rectagles' borders
        "line_width": 0,  # Width of the rectagles' borders
        "legend_x_label": "Higher x value",  # x variable label for the legend
        "legend_y_label": "Higher y value",  # y variable label for the legend
        "legend_font_size": 11,  # Legend font size
        "legend_font_color": "#333",  # Legend font color
    }

    # Calculate height
    conf["height"] = conf["width"] * conf["ratio"]

    return conf


"""
Function to recalculate values in case width is changed
"""


def recalc_vars(new_width, variables, conf=conf_defaults()):

    # Calculate the factor of the changed width
    factor = new_width / 1000

    # Apply factor to all variables that have been passed to the function
    for var in variables:
        if var == "map_zoom":
            # Calculate the zoom factor
            # Mapbox zoom is based on a log scale. map_zoom needs to be set
            # to value ideal for our map at 1000px.
            # So factor = 2 ^ (zoom - map_zoom) and zoom = log(factor) / log(2) + map_zoom
            conf[var] = math.log(factor) / math.log(2) + conf[var]
        else:
            conf[var] = conf[var] * factor

    return conf


"""
Function to load GeoJSON file with geographical data of the entities
"""


def load_geojson(geojson_url, data_dir="data", local_file=False):

    # Make sure data_dir is a string
    data_dir = str(data_dir)

    # Set name for the file to be saved
    if not local_file:
        # Use original file name if none is specified
        url_parsed = urlparse(geojson_url)
        local_file = os.path.basename(url_parsed.path)

    geojson_file = data_dir + "/" + str(local_file)

    # Create folder for data if it does not exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Download GeoJSON in case it doesn't exist
    if not os.path.exists(geojson_file):

        # Make http request for remote file data
        geojson_request = requests.get(geojson_url)

        # Save file to local copy
        with open(geojson_file, "wb") as file:
            file.write(geojson_request.content)

    # Load GeoJSON file
    geojson = json.load(open(geojson_file, "r"))

    # Return GeoJSON object
    return geojson


"""
Function that assigns a value (x) to one of three bins (0, 1, 2).
The break points for the bins can be defined by break_1 and break_2.
"""


def set_interval_value(x, break_1, break_2):
    if x <= break_1:
        return 0
    elif break_1 < x <= break_2:
        return 1
    else:
        return 2


"""
Function that adds a column 'biv_bins' to the dataframe containing the 
position in the 9-color matrix for the bivariate colors
    
Arguments:
    df: Dataframe
    x: Name of the column containing values of the first variable
    y: Name of the column containing values of the second variable

"""


def prepare_df(df, x="x", y="y"):

    # Check if arguments match all requirements
    if df[x].shape[0] != df[y].shape[0]:
        raise ValueError(
            "ERROR: The list of x and y coordinates must have the same length."
        )

    # Calculate break points at percentiles 33 and 66
    x_breaks = np.percentile(df[x], [33, 66])
    y_breaks = np.percentile(df[y], [33, 66])

    # Assign values of both variables to one of three bins (0, 1, 2)
    x_bins = [
        set_interval_value(value_x, x_breaks[0], x_breaks[1]) for value_x in df[x]
    ]
    y_bins = [
        set_interval_value(value_y, y_breaks[0], y_breaks[1]) for value_y in df[y]
    ]

    # Calculate the position of each x/y value pair in the 9-color matrix of bivariate colors
    df["biv_bins"] = [
        int(value_x + 3 * value_y) for value_x, value_y in zip(x_bins, y_bins)
    ]

    return df


"""
Function to create a color square containig the 9 colors to be used as a legend
"""


def create_legend(fig, colors, conf=conf_defaults()):

    # Reverse the order of colors
    legend_colors = colors[:]
    legend_colors.reverse()

    # Calculate coordinates for all nine rectangles
    coord = []

    # Adapt height to ratio to get squares
    width = conf["box_w"]
    height = conf["box_h"] / conf["ratio"]

    # Start looping through rows and columns to calculate corners the squares
    for row in range(1, 4):
        for col in range(1, 4):
            coord.append(
                {
                    "x0": round(conf["right"] - (col - 1) * width, 4),
                    "y0": round(conf["top"] - (row - 1) * height, 4),
                    "x1": round(conf["right"] - col * width, 4),
                    "y1": round(conf["top"] - row * height, 4),
                }
            )

    # Create shapes (rectangles)
    for i, value in enumerate(coord):
        # Add rectangle
        fig.add_shape(
            go.layout.Shape(
                type="rect",
                fillcolor=legend_colors[i],
                line=dict(
                    color=conf["line_color"],
                    width=conf["line_width"],
                ),
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                x0=coord[i]["x0"],
                y0=coord[i]["y0"],
                x1=coord[i]["x1"],
                y1=coord[i]["y1"],
            )
        )

        # Add text for first variable
        fig.add_annotation(
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="top",
            x=coord[8]["x1"],
            y=coord[8]["y1"],
            showarrow=False,
            text=conf["legend_x_label"] + " -->",
            font=dict(
                color=conf["legend_font_color"],
                size=conf["legend_font_size"],
            ),
            borderpad=0,
        )

        # Add text for second variable
        fig.add_annotation(
            xref="paper",
            yref="paper",
            xanchor="right",
            yanchor="bottom",
            x=coord[8]["x1"],
            y=coord[8]["y1"],
            showarrow=False,
            text=conf["legend_y_label"] + " -->",
            font=dict(
                color=conf["legend_font_color"],
                size=conf["legend_font_size"],
            ),
            textangle=270,
            borderpad=0,
        )

    return fig


"""
Function to create the map

Arguments:
    df: The dataframe that contains all the necessary columns
    colors: List of 9 blended colors
    x: Name of the column that contains values of first variable (defaults to 'x')
    y: Name of the column that contains values of second variable (defaults to 'y')
    ids: Name of the column that contains ids that connect the data to the GeoJSON (defaults to 'id')
    name: Name of the column conatining the geographic entity to be displayed as a description (defaults to 'name')
"""


def create_bivariate_map(
    df, colors, geojson, x="x", y="y", ids="id", name="name", conf=conf_defaults()
):

    if len(colors) != 9:
        raise ValueError(
            "ERROR: The list of bivariate colors must have a length eaqual to 9."
        )

    # Recalculate values if width differs from default
    if not conf["width"] == 1000:
        conf = recalc_vars(
            conf["width"],
            ["height", "plot_title_size", "legend_font_size", "map_zoom"],
            conf,
        )

    # Prepare the dataframe with the necessary information for our bivariate map
    df_plot = prepare_df(df, x, y)

    # Create the figure
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=geojson,
            locations=df_plot[ids],
            z=df_plot["biv_bins"],
            marker_line_width=0.5,
            colorscale=[
                [0 / 8, colors[0]],
                [1 / 8, colors[1]],
                [2 / 8, colors[2]],
                [3 / 8, colors[3]],
                [4 / 8, colors[4]],
                [5 / 8, colors[5]],
                [6 / 8, colors[6]],
                [7 / 8, colors[7]],
                [8 / 8, colors[8]],
            ],
            customdata=df_plot[
                [name, ids, x, y]
            ],  # Add data to be used in hovertemplate
            hovertemplate="<br>".join(
                [  # Data to be displayed on hover
                    "<b>%{customdata[0]}</b> (ID: %{customdata[1]})",
                    conf["hover_x_label"] + ": %{customdata[2]}",
                    conf["hover_y_label"] + ": %{customdata[3]}",
                    "<extra></extra>",  # Remove secondary information
                ]
            ),
        )
    )

    # Add some more details
    fig.update_layout(
        title=dict(
            text=conf["plot_title"],
            font=dict(
                size=conf["plot_title_size"],
            ),
            x=0.5,  # Centra el título horizontalmente
            xanchor="center",  # Asegura que el ancla esté centrada
            y=0.95,  # Baja el título si es necesario (puedes ajustar este valor)
        ),
        mapbox_style="white-bg",
        width=conf["width"],
        height=conf["height"],
        autosize=True,
        mapbox=dict(
            center=dict(
                lat=conf["center_lat"], lon=conf["center_lon"]
            ),  # Centro del mapa
            zoom=conf["map_zoom"],  # Zoom del mapa
        ),
    )

    fig.update_traces(
        marker_line_width=conf[
            "borders_width"
        ],  # Width of the geographic entity borders
        marker_line_color=conf[
            "borders_color"
        ],  # Color of the geographic entity borders
        showscale=False,  # Hide the colorscale
    )

    # Add the legend
    fig = create_legend(fig, colors, conf)

    return fig


# Define sets of 9 colors to be used
# Order: bottom-left, bottom-center, bottom-right, center-left, center-center, center-right, top-left, top-center, top-right
color_sets = {
    "pink-blue": [
        "#e8e8e8",
        "#ace4e4",
        "#5ac8c8",
        "#dfb0d6",
        "#a5add3",
        "#5698b9",
        "#be64ac",
        "#8c62aa",
        "#3b4994",
    ],
    "teal-red": [
        "#e8e8e8",
        "#e4acac",
        "#c85a5a",
        "#b0d5df",
        "#ad9ea5",
        "#985356",
        "#64acbe",
        "#627f8c",
        "#574249",
    ],
    "blue-organe": [
        "#fef1e4",
        "#fab186",
        "#f3742d",
        "#97d0e7",
        "#b0988c",
        "#ab5f37",
        "#18aee5",
        "#407b8f",
        "#5c473d",
    ],
}

# Load your CSV file
df_data = pd.read_csv(
    "/Users/alverjoanperezcuellar/Desktop/Cal-map/Cal-u-Rates-for-map.csv"
)


# Prepare 'x' (Unemployment Rate) and 'y' (Rate H.S. Diploma)
df_x = df_data[["County", "Unemployment-Rate"]].copy()
df_y = df_data[["County", "Rate H.S. Diploma or Less"]].copy()

# Rename columns to 'id', 'x', 'y', and 'name' to match the format in the tutorial
df_x = df_x.rename(columns={"County": "id", "Unemployment-Rate": "x"})
df_y = df_y.rename(columns={"County": "id", "Rate H.S. Diploma or Less": "y"})

# Merge both dataframes
df = pd.merge(df_x, df_y[["id", "y"]], how="left", on="id")

# Check merged dataframe
df.head()

# Path to your local GeoJSON file
geojson_path = "./California_County_Boundaries_6550485670014028237.geojson"

# Load the GeoJSON data
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Check available keys in 'properties'
print(geojson_data["features"][0]["properties"].keys())  # Inspect available keys

# Assign the correct key based on the above output
for i in range(len(geojson_data["features"])):
    geojson_data["features"][i]["id"] = geojson_data["features"][i]["properties"].get(
        "COUNTY_NAME", None
    )


# Confirm the changes by printing part of the updated geojson data
print(geojson_data["features"][0]["id"])  # Check if 'id' is set correctly

# Now you can proceed with creating the map using Plotly's choropleth_mapbox.

# Load default configuration (you'll need to implement a conf_defaults() function if it doesn't exist)
conf = conf_defaults()

# Customizing the map and legend titles and other attributes for your specific case:
conf["plot_title"] = "California H.S. Diploma or Less Rate vs Unemployment Rate"

conf["hover_x_label"] = (
    "Unemployment Rate (%)"  # Label to appear on hover for the x variable
)
conf["hover_y_label"] = (
    "Rate of High School Diploma Holders (%)"  # Label to appear on hover for the y variable
)
conf["width"] = 1000  # Set the width of the map
conf["center_lat"] = 37.5  # Approximate latitude for California
conf["center_lon"] = -119  # Approximate longitude for California
conf["map_zoom"] = 5.5  # Appropriate zoom level for California's map
conf["borders_width"] = 1  # Adjust the border width of counties for clarity

# Define settings for the legend (adjust to your preferences)
conf["top"] = 0.85  # Adjust vertical position of the top right corner of the legend
conf["right"] = 0.70  # Adjust horizontal position of the top right corner of the legend
conf["line_width"] = 1  # Width of the rectangle borders in the legend
conf["legend_x_label"] = "Unemployment"  # Label for the x-axis in the legend
conf["legend_y_label"] = (
    "High School Diploma<br>or Less"  # Label for the y-axis in the legend
)

# Assuming 'x' refers to the unemployment rate and 'y' refers to the rate of high school diploma attainment
# Adjusting the names of the columns and passing the geojson data

fig = create_bivariate_map(
    df,
    color_sets["pink-blue"],  # Choose a color set for your bivariate map
    geojson_data,  # The geojson data loaded for California counties
    x="x",  # Unemployment rate from your dataframe
    y="y",  # High school diploma attainment rate from your dataframe
    ids="id",  # The column representing the county IDs
    name="id",  # County names (ensure you use the correct column name if different)
    conf=conf,  # Configuration object defined previously
)

# Set the map center around California and adjust zoom
conf["center_lat"] = 37.7749  # Latitude of California
conf["center_lon"] = -119.4194  # Longitude of California
conf["map_zoom"] = 5.5  # Adjust the zoom to better fit the state

print(geojson_data["features"][i]["properties"].keys())

fig.update_layout(mapbox_style="carto-positron")
fig.show()
