import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
import random

# Utility Function: Blend a color with white
def blend_with_white(color, alpha):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    r = int(r + (255 - r) * alpha)
    g = int(g + (255 - g) * alpha)
    b = int(b + (255 - b) * alpha)

    return "#{:02X}{:02X}{:02X}".format(r, g, b)

# Function to generate node and link colors
def generate_colors(base_colors, num_shades):
    return [blend_with_white(random.choice(base_colors), random.uniform(0.3, 0.7)) for _ in range(num_shades)]

# Function to preprocess data and extract unique values
def preprocess_data(file_path):
    data = pd.read_csv(file_path)

    # Get unique values and sort them
    models = sorted(data['Model'].unique().tolist())
    countries = sorted(data['Country'].unique().tolist())
    institutes = sorted(data['Institute'].unique().tolist())
    portals = sorted(data['Portal'].unique().tolist())
    downscaling = sorted(data['Downscaling'].unique().tolist())
    labels = models + countries + institutes + portals + downscaling

    return data, models, countries, institutes, portals, labels

# Function to reorder the main categories
def reorder_categories(data, category_order):
    """
    Reorder the main categories (Model, Country, Institute, Portal).

    Args:
        data (pd.DataFrame): The input data.
        category_order (list): List specifying the order of the categories, e.g., ['Country', 'Model', 'Institute', 'Portal'].

    Returns:
        tuple: Updated labels and adjusted data mapping for categories.
    """
    all_categories = {
        'Model': sorted(data['Model'].unique().tolist()),
        'Country': sorted(data['Country'].unique().tolist()),
        'Institute': sorted(data['Institute'].unique().tolist()),
        'Portal': sorted(data['Portal'].unique().tolist()),
        'Downscaling': sorted(data['Downscaling'].unique().tolist()),
    }

    reordered_labels = []
    mapping = {}
    offset = 0

    for category in category_order:
        if category in all_categories:
            category_values = all_categories[category]
            reordered_labels.extend(category_values)
            mapping[category] = (category_values, offset)
            offset += len(category_values)

    return reordered_labels, mapping

# Function to create Sankey paths
def create_paths(data, mapping, category_order, highlight_country=None):
    source, target, value, link_colors = [], [], [], []

    for _, row in data.iterrows():
        country_color = "lightgray"  # Default color

        # Highlight specific country if needed
        if highlight_country and row['Country'] == highlight_country:
            country_color = "#003C86"

        # Iterate through the category order to create paths
        for i in range(len(category_order) - 1):
            current_category = category_order[i]
            next_category = category_order[i + 1]

            current_values, current_offset = mapping[current_category]
            next_values, next_offset = mapping[next_category]

            source.append(current_offset + current_values.index(row[current_category]))
            target.append(next_offset + next_values.index(row[next_category]))
            value.append(1)
            link_colors.append(country_color)

    return source, target, value, link_colors

# Function to create and plot Sankey diagram
def create_sankey_figure(labels, node_colors, source, target, value, link_colors, title):
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        )
    )])

    fig.update_layout(title_text=title, font_size=10)
    return fig

# Main function to orchestrate the Sankey diagram creation
def main(file_path, highlight_country=None, category_order=None, output_file="Sankey_Diagram.html"):
    base_colors = ['#68023F', '#008169', '#EF0096', '#00DCB5', '#FFCFE2', '#003C86', '#9400E6', '#009FFA',
                   '#FF71FD', '#7CFFFA', '#6A0213', '#008607', '#F60239', '#00E307', '#FFDC3D']

    # Preprocess data
    data = pd.read_csv(file_path)

    # Reorder categories if specified
    if category_order:
        labels, mapping = reorder_categories(data, category_order)
    else:
        category_order = ['Model', 'Country', 'Institute', 'Portal', 'Downscaling']
        labels, mapping = reorder_categories(data, category_order)

    # Generate colors for nodes and links
    node_colors = generate_colors(base_colors, len(labels))

    # Create paths
    source, target, value, link_colors = create_paths(data, mapping, category_order, highlight_country)

    # Create Sankey diagram
    title = f"{' - '.join(category_order)} Relationships{' with ' + highlight_country + ' Highlighted' if highlight_country else ''}"
    fig = create_sankey_figure(labels, node_colors, source, target, value, link_colors, title)

    # Show and save the figure
    fig.show()
    pyo.plot(fig, filename=output_file)

# Example usage
if __name__ == "__main__":
    file_path = "/Users/asadehaan/PycharmProjects/GCM-associations/GCM_Association_data_1_8_25.csv"
    highlight_country = None  # Set to None if no specific country needs to be highlighted
    category_order = ['Country', 'Institute', 'Model', 'Downscaling', 'Portal']  # Specify the desired order of main categories
    main(file_path, highlight_country, category_order)
