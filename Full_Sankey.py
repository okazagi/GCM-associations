import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
import random

# set up the color scheme
# Set color palette, colorblind friendly
portal_colors = ['#68023F', '#008169', '#EF0096', '#00DCB5', '#FFCFE2', '#003C86', '#9400E6', '#009FFA',
                 '#FF71FD', '#7CFFFA', '#6A0213', '#008607', '#F60239', '#00E307', '#FFDC3D']

def blend_with_white(color, alpha):
    """
    Blend a color with white. There are a lot of nodes in this Sankey diagram so we need to create a lot of shades of colors in the colorblind friendly palette.
    
    Args:
    - color (str): Hexadecimal color string (e.g., "#FF0000" for red).
    - alpha (float): Blending factor between 0 and 1. 
        0 will give original color, 1 will give white.

    Returns:
    - str: Hexadecimal color string after blending.
    """
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    r = int(r + (255 - r) * alpha)
    g = int(g + (255 - g) * alpha)
    b = int(b + (255 - b) * alpha)
    
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

colors = [ "#68023F", "#008169", "#EF0096", "#00DCB5", "#FFCFE2", "#003C86", "#9400E6", "#009FFA", 
          "#FF71FD", "#7CFFFA", "#6A0213", "#008607", "#F60239", "#00E307", "#FFDC3D"]

# Assign base colors to portals
portal_colors = colors

# Generate shades for the other nodes
other_node_colors = [blend_with_white(random.choice(colors), random.uniform(0.3, 0.7)) for _ in range(174)]

node_colors = other_node_colors + portal_colors 

# Read in the data
data = pd.read_csv('path/to/file.csv')

#get the unique values from the columns
institutes = data['Institute'].unique().tolist()
models = data['Model'].unique().tolist()
portals = data['Portal'].unique().tolist()
countries = data['Country'].unique().tolist()

#sort the unique values
models = sorted(models)
countries = sorted(countries)
institutes = sorted(institutes)
portals = sorted(portals)

# Create a list of labels
labels = models + countries + institutes + portals

# Get source, target, value, and color lists
source = []
target = []
value = []
link_colors = []

"""The following code creates the Sankey diagram. It creates a link from the model to the country, and allows you to highlight a specific country (in this case, the USA) by changing the color of the links that involve that country.
It can be easily modified to highlight a different node (e.g., a specific model, institute, or portal) by changing the color of the corresponding links."""

# First, create all non-USA paths
for _, row in data.iterrows():
    if row['Country'] != 'USA':
        # Link from model to country
        source.append(models.index(row['Model']))
        target.append(len(models) + countries.index(row['Country']))
        value.append(1)  # you can change this value if needed
        link_colors.append('lightgray')

        # Link from country to institute
        source.append(len(models) + countries.index(row['Country']))
        target.append(len(models) + len(countries) + institutes.index(row['Institute']))
        value.append(1)  # assuming each row in the csv represents a count of 1
        link_colors.append('lightgray')

        # Link from institute to portal
        source.append(len(models) + len(countries) + institutes.index(row['Institute']))
        target.append(len(models) + len(countries) + len(institutes) + portals.index(row['Portal']))
        value.append(1)
        link_colors.append('lightgray')

# Then, create all USA paths
for _, row in data.iterrows():
    if row['Country'] == 'USA':
        # Link from model to country
        source.append(models.index(row['Model']))
        target.append(len(models) + countries.index(row['Country']))
        value.append(1)
        link_colors.append('#003C86')

        # Link from country to institute
        source.append(len(models) + countries.index(row['Country']))
        target.append(len(models) + len(countries) + institutes.index(row['Institute']))
        value.append(1)
        link_colors.append('#003C86')

        # Link from institute to portal
        source.append(len(models) + len(countries) + institutes.index(row['Institute']))
        target.append(len(models) + len(countries) + len(institutes) + portals.index(row['Portal']))
        value.append(1)
        link_colors.append('#003C86')

# Plot the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors  # use the set node colors
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors  # set color based on USA connection
    )
)])

fig.update_layout(title_text="Model - Country - Institute - Portal Relationships with USA Highlighted", font_size=10)
fig.show()
pyo.plot(fig, filename='USA_Sankey.html')
