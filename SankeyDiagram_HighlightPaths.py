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
    models = sorted(data['Model'].unique().tolist())
    countries = sorted(data['Country'].unique().tolist())
    institutes = sorted(data['Institute'].unique().tolist())
    portals = sorted(data['Portal'].unique().tolist())
    downscaling = sorted(data['Downscaling'].unique().tolist())
    labels = models + countries + institutes + portals + downscaling
    return data, models, countries, institutes, portals, labels


# Function to reorder the main categories
def reorder_categories(data, category_order):
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


def create_sankey_figure(labels, node_colors, source, target, value, link_colors, title):
    fig = go.Figure(data=[go.Sankey(
        arrangement='freeform',
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

    fig.update_layout(
        width=1800,  # Adjust width
        height=1300,  # Adjust height
        title_text=title,
        font_size=12
    )

    return fig


def create_paths_and_colors(data, mapping, category_order, highlight_path=None, highlight_column=None):
    base_colors = ['#68023F', '#008169', '#EF0096', '#00DCB5', '#FFCFE2', '#003C86', '#9400E6', '#009FFA']
    source, target, value, link_colors = [], [], [], []
    node_colors = []

    # Assign colors for nodes
    for category in category_order:
        category_values, _ = mapping[category]
        generated_colors = generate_colors(base_colors, len(category_values))
        node_colors.extend(generated_colors)

    # Generate link paths and colors
    for _, row in data.iterrows():
        for i in range(len(category_order) - 1):
            current_category = category_order[i]
            next_category = category_order[i + 1]

            current_values, current_offset = mapping[current_category]
            next_values, next_offset = mapping[next_category]

            # Determine the color for the link
            if highlight_path and highlight_column and row[highlight_column] == highlight_path:
                link_color = "#0032A0"  # Highlight links associated with the highlighted path
            else:
                link_color = "lightgray"  # Default color

            source.append(current_offset + current_values.index(row[current_category]))
            target.append(next_offset + next_values.index(row[next_category]))
            value.append(1)
            link_colors.append(link_color)

    return source, target, value, link_colors, node_colors


def main(file_path, highlight_path=None, highlight_column=None, category_order=None, output_file="Sankey_Diagram.html"):
    # Preprocess data
    data = pd.read_csv(file_path)

    # Reorder categories if specified
    if category_order:
        labels, mapping = reorder_categories(data, category_order)
    else:
        category_order = ['Model', 'Country', 'Institute', 'Portal', 'Downscaling']
        labels, mapping = reorder_categories(data, category_order)

    # Create paths and colors
    source, target, value, link_colors, node_colors = create_paths_and_colors(
        data, mapping, category_order, highlight_path=highlight_path, highlight_column=highlight_column
    )

    # Create Sankey diagram
    title = f"{' - '.join(category_order)} Relationships"
    if highlight_path and highlight_column:
        title += f" (Highlighting {highlight_column}: {highlight_path})"

    fig = create_sankey_figure(labels, node_colors, source, target, value, link_colors, title)

    # Save the figure as an HTML file
    fig.write_html(output_file)
    print(f"Sankey diagram saved as {output_file}")

    # Show the figure
    fig.show()


if __name__ == "__main__":
    file_path = "/Users/asadehaan/PycharmProjects/GCM-associations/GCM_Association_data.csv"
    category_order = ['Portal', 'Downscaling', 'Model', 'Institute', 'Country']
    
    # Customize highlights
    highlight_column = "Institute"  # Column to highlight (can be 'Country', 'Institute', 'Model', etc.)
    highlight_path = "NASA"       # Value to highlight in the specified column
    
    main(file_path, highlight_path=highlight_path, highlight_column=highlight_column, category_order=category_order)

