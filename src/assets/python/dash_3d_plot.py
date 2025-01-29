# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    dash_3d_plot.py
# Date Created: 2024-09-13
#
# Description: This Dash app connects to a MySQL database to retrieve demographic data
#              from the 'census_zipcode_demographics_2022' table. It performs t-SNE 
#              dimensionality reduction on the data and creates a 3D visualization 
#              using Plotly. The visualization shows CBU ZIP codes in light blue and 
#              the 50 most demographically similar non-CBU ZIP codes in yellow.
#
# Usage: Run this Dash app to generate the 3D t-SNE plot. Ensure the environment
#        variables for MySQL connection are properly set in '.env.local'.
# --------------------------------------------------------------------------------



import json
import numpy as np
import plotly.graph_objs as go
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# Load data from the CSV file
csv_file_path = 'census_zipcode_percentages.csv'
full_census_data = pd.read_csv(csv_file_path)

# Ensure Zip_Code is treated as a string and remove leading/trailing spaces
full_census_data['Zip_Code'] = full_census_data['Zip_Code'].astype(str).str.strip()

# Replace NULL (NaN) values with 0 or the median, depending on the column's type
full_census_data.fillna({
    'Population': 0,
    'Median_Income': full_census_data['Median_Income'].median(),
    'Bachelor_Degree': 0,
    'Graduate_Professional_Degree': 0,
    'White_Alone': 0,
    'Black_Alone': 0,
    'Hispanic_Latino': 0,
    'Unemployment': full_census_data['Unemployment'].median(),
    'Median_Home_Value': full_census_data['Median_Home_Value'].median()
}, inplace=True)

# List of CBU student zip codes
cbu_zipcodes = [
    '92503', '92504', '92508', '92506', '92880', '92571', '92336', '92509',
    '92882', '92399', '92881', '92505', '92223', '92557', '92553', '92555',
    '91709', '92879', '92584', '92883', '92507', '92374', '92562', '91752',
    '91710', '92335', '92570', '92407', '92324', '91739', '92592', '92376',
    '92563', '92346', '92373', '92860', '92530', '92337', '92551', '91761',
    '92404', '91737', '92532', '92544', '91762', '92308', '92545', '92392',
    '91701', '92583'
]

# Filter the census data for CBU zip codes
cbu_census_data = full_census_data[full_census_data['Zip_Code'].isin(cbu_zipcodes)]

# Relevant demographic features for clustering
features = ['Population', 'Median_Income', 'Bachelor_Degree', 'Graduate_Professional_Degree',
            'White_Alone', 'Black_Alone', 'Hispanic_Latino', 'Unemployment', 'Median_Home_Value']

# Standardize the data
scaler = StandardScaler()
cbu_census_data_scaled = scaler.fit_transform(cbu_census_data[features])

# Find non-CBU zip codes
non_cbu_census_data = full_census_data[~full_census_data['Zip_Code'].astype(str).isin(cbu_zipcodes)]
non_cbu_census_data_scaled = scaler.transform(non_cbu_census_data[features])

# Compute Euclidean distance between non-CBU zip codes and the centroid of the CBU zip codes
cbu_centroid = np.mean(cbu_census_data_scaled, axis=0)
distances = euclidean_distances(non_cbu_census_data_scaled, [cbu_centroid])

# Get indices of the 50 closest non-CBU zip codes based on demographic similarity
top_50_indices = np.argsort(distances, axis=0)[:50].flatten()

# Select the top 50 most similar non-CBU zip codes
top_50_non_cbu_census_data = non_cbu_census_data.iloc[top_50_indices]
top_50_non_cbu_census_data_scaled = non_cbu_census_data_scaled[top_50_indices]

# Perform t-SNE to reduce the data to 3D for both datasets
tsne = TSNE(n_components=3, random_state=42, perplexity=5, init='random')
combined_data_scaled = np.vstack([cbu_census_data_scaled, top_50_non_cbu_census_data_scaled])
combined_coords = tsne.fit_transform(combined_data_scaled)

# Extract CBU and top 50 non-CBU coordinates
cbu_coords = combined_coords[:len(cbu_census_data)]
non_cbu_coords = combined_coords[len(cbu_census_data):]

def generate_hover_info(data):
    hover_info = []
    for i, row in data.iterrows():
        hover_text = f"ZIP: {row['Zip_Code']}<br>" \
                     f"Population: {int(row['Population'])}<br>" \
                     f"Median Income: {int(row['Median_Income'])}<br>" \
                     f"Education (Bachelors): {row['Bachelor_Degree']:.1f}<br>" \
                     f"Unemployment: {row['Unemployment']:.1f}<br>" \
                     f"Median Home Value: {int(row['Median_Home_Value'])}"
        hover_info.append(hover_text)
    return hover_info

cbu_hover_info = generate_hover_info(cbu_census_data)
non_cbu_hover_info = generate_hover_info(top_50_non_cbu_census_data)

# Create the initial 3D plot
def create_3d_plot(cbu_coords, non_cbu_coords):
    trace_cbu = go.Scatter3d(
        x=cbu_coords[:, 0],
        y=cbu_coords[:, 1],
        z=cbu_coords[:, 2],
        mode='markers+text',
        marker=dict(
            size=6,
            color='rgb(0, 213, 240)', # light blue
            opacity=0.8
        ),
        text=cbu_census_data['Zip_Code'],
        hoverinfo='text',
        hovertext=cbu_hover_info,
        name='CBU'
    )

    trace_non_cbu = go.Scatter3d(
        x=non_cbu_coords[:, 0],
        y=non_cbu_coords[:, 1],
        z=non_cbu_coords[:, 2],
        mode='markers+text',
        marker=dict(
            size=6,
            color='rgb(235,216,1)', # gold yellow
            opacity=0.8
        ),
        text=top_50_non_cbu_census_data['Zip_Code'],
        hoverinfo='text',
        hovertext=non_cbu_hover_info,
        name='Non-CBU'
    )

    layout = go.Layout(
        scene=dict(
            xaxis_title='t-SNE Component 1',
            yaxis_title='t-SNE Component 2',
            zaxis_title='t-SNE Component 3'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True
    )

    return go.Figure(data=[trace_cbu, trace_non_cbu], layout=layout)

app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div([

        # Sidebar with filter options
        html.Div([
            html.Button("☰", id="toggle-button", n_clicks=0, style={
                'position': 'absolute', 
                'top': '10px', 
                'left': '10px',
                'font-size': '24px', 
                'cursor': 'pointer', 
                'background-color': 'lightgray', 
                'z-index': '2',
            }),
            
            html.Div([


                html.Div([
                    html.Label("Select Demographic Dimension:"),
                    dcc.Dropdown(
                        id='dimension-dropdown',
                        options=[
                            {'label': 'Generalized', 'value': 'generalized'},
                            {'label': 'Economic Prosperity', 'value': 'economic_prosperity'},
                            {'label': 'Educational Attainment', 'value': 'educational_attainment'},
                            {'label': 'Population Density and Urbanization', 'value': 'population_density'},
                            {'label': 'Ethnic Diversity', 'value': 'ethnic_diversity'}
                        ],
                        value='generalized'  # Default value
                    )
                ], style={'margin-top': '3vw'}),  # Adjust spacing as needed
                html.Div([
                    html.Label("Select Feature to Filter By:"),
                    dcc.Dropdown(
                        id='feature-dropdown',
                        options=[
                            {'label': 'Population', 'value': 'Population'},
                            {'label': 'Median Income', 'value': 'Median_Income'},
                            {'label': 'Education (Bachelors)', 'value': 'Bachelor_Degree'},
                            {'label': 'Unemployment', 'value': 'Unemployment'},
                            {'label': 'Median Home Value', 'value': 'Median_Home_Value'}
                        ],
                        value='Population'  # Default value
                    )
                ], style={'margin-top': '3vw'}),  # Add spacing above the dropdown

                html.Div([
                    html.Label(id='slider-label', children="Filter by Population Range:"),
                    dcc.RangeSlider(
                        id='feature-slider',
                        min=0,  # Replace with dynamic min value
                        max=1000000,  # Replace with dynamic max value
                        step=1000,
                        marks={int(i): str(int(i)) for i in np.linspace(0, 1000000, num=10)},
                        value=[0, 1000000]
                    )
                ], style={'margin-top': '20px'}),  # Add spacing above the slider
                
            ], id="sidebar", style={
                'width': '250px', 
                'height': '100%', 
                'position': 'absolute',
                'top': '0', 
                'left': '-250px', 
                'background-color': '#f8f9fa',
                'padding': '10px', 
                'transition': '0.3s', 
                'z-index': '1', 
                'overflow': 'auto'
            }),
        ]),

        # Main content (Graph)
        html.Div([
            dcc.Graph(id='tsne-plot', figure=create_3d_plot(cbu_coords, non_cbu_coords), style={'height': '90vh'})
        ], id='graph-container', style={'position': 'relative', 'padding-left': '10px'})
    ])
])

@app.callback(
    [Output('feature-slider', 'min'),
     Output('feature-slider', 'max'),
     Output('feature-slider', 'value'),
     Output('feature-slider', 'marks'),
     Output('slider-label', 'children')],
    [Input('feature-dropdown', 'value')]
)
def update_slider(selected_feature):
    # Fields that are percentage-based
    percentage_fields = ['Bachelor_Degree', 'Unemployment']
    
    # Format values in thousands for these fields
    fields_in_thousands = ['Population', 'Median_Income', 'Median_Home_Value']

    if selected_feature in percentage_fields:
        # Set range for percentage fields (0 to 1)
        min_val, max_val = 0, 1
        value = [min_val, max_val]
        marks = {i / 10: f"{int(i * 10)}" for i in range(0, 11)}  # Marks from 0% to 100%
        label = f"{selected_feature.replace('_', ' ')} Percentage %:"
    else:
        # Use min and max values for non-percentage fields
        min_val = full_census_data[selected_feature].min()
        max_val = full_census_data[selected_feature].max()
        value = [min_val, max_val]

        # Format marks for fields in thousands
        if selected_feature in fields_in_thousands:
            marks = {int(i): f"{int(i/1000)}" for i in np.linspace(min_val, max_val, num=10)}
        else:
            marks = {int(i): str(int(i)) for i in np.linspace(min_val, max_val, num=10)}

        label = f" {selected_feature.replace('_', ' ')} (in thousands):"
    
    return min_val, max_val, value, marks, label

# Callback to update the graph based on the selected feature and slider range
@app.callback(
    Output('tsne-plot', 'figure'),
    [Input('dimension-dropdown', 'value'),  # New input for the dimension dropdown
     Input('feature-dropdown', 'value'),
     Input('feature-slider', 'value')]
)
def update_3d_graph(selected_dimension, selected_feature, feature_range):
    # Default axis data and labels for Generalized (combined t-SNE components)
    x_data, y_data, z_data = combined_coords[:, 0], combined_coords[:, 1], combined_coords[:, 2]
    xaxis_title, yaxis_title, zaxis_title = 't-SNE Component 1', 't-SNE Component 2', 't-SNE Component 3'

    # Update data and labels based on selected dimension
    if selected_dimension == 'economic_prosperity':
        x_data = full_census_data['Median_Income']
        y_data = full_census_data['Median_Home_Value']
        z_data = full_census_data['Population']
        xaxis_title, yaxis_title, zaxis_title = 'Median Income', 'Median Home Value', 'Population'
    elif selected_dimension == 'educational_attainment':
        x_data = full_census_data['Bachelor_Degree']
        y_data = full_census_data['Graduate_Professional_Degree']
        z_data = full_census_data['Unemployment']
        xaxis_title, yaxis_title, zaxis_title = 'Bachelor’s Degree %', 'Graduate Degree %', 'Unemployment Rate'
    elif selected_dimension == 'population_density':
        x_data = full_census_data['Population']
        y_data = full_census_data['Unemployment']
        z_data = full_census_data['Median_Home_Value']
        xaxis_title, yaxis_title, zaxis_title = 'Population', 'Unemployment Rate', 'Median Home Value'
    elif selected_dimension == 'ethnic_diversity':
        x_data = full_census_data['Hispanic_Latino']
        y_data = full_census_data['Black_Alone']
        z_data = full_census_data['Population']
        xaxis_title, yaxis_title, zaxis_title = 'Hispanic or Latino %', 'Black or African American %', 'Population'


    # Apply feature-based filtering
    filtered_cbu_data = cbu_census_data[
        (cbu_census_data[selected_feature] >= feature_range[0]) & 
        (cbu_census_data[selected_feature] <= feature_range[1])
    ]
    filtered_non_cbu_data = top_50_non_cbu_census_data[
        (top_50_non_cbu_census_data[selected_feature] >= feature_range[0]) & 
        (top_50_non_cbu_census_data[selected_feature] <= feature_range[1])
    ]

    # Generate updated coordinates
    filtered_cbu_coords = np.column_stack((x_data[:len(filtered_cbu_data)], 
                                           y_data[:len(filtered_cbu_data)], 
                                           z_data[:len(filtered_cbu_data)]))
    filtered_non_cbu_coords = np.column_stack((x_data[len(filtered_cbu_data):len(filtered_cbu_data) + len(filtered_non_cbu_data)], 
                                               y_data[len(filtered_cbu_data):len(filtered_cbu_data) + len(filtered_non_cbu_data)], 
                                               z_data[len(filtered_cbu_data):len(filtered_cbu_data) + len(filtered_non_cbu_data)]))
    
        # Create the plot figure and update axis titles
    figure = create_3d_plot(filtered_cbu_coords, filtered_non_cbu_coords)
    figure.update_layout(
        scene=dict(
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            zaxis_title=zaxis_title
        )
    )
    return figure

# Sidebar toggle callback
@app.callback(
    [Output("sidebar", "style"),
     Output("graph-container", "style")],
    [Input("toggle-button", "n_clicks")],
    [State("sidebar", "style"), State("graph-container", "style")]
)
def toggle_sidebar(n_clicks, sidebar_style, graph_style):
    if n_clicks % 2 == 1:
        # Show sidebar and move graph to the right
        sidebar_style["left"] = "0vw"
        graph_style["padding-left"] = "0vw"  # Move graph to the right when sidebar is open
        graph_style["padding-top"] = "2.5vw"  # Add padding-top when sidebar is open
        sidebar_style["display"] = "block"  # Show the graph


    else:
        # Hide sidebar and reset graph position
        # sidebar_style["left"] = "-17vw"
        graph_style["padding-left"] = "0vw"  # Reset padding when sidebar is closed
        graph_style["padding-top"] = "2.5vw"  # Add padding-top when sidebar is open
        sidebar_style["display"] = "none"  # Hide the graph

    return sidebar_style, graph_style


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
