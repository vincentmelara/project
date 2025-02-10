# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    top15_2d_plot.py
# Date Created: 2024-09-13
#
# Description: This script connects to a MySQL database to retrieve demographic data
#              from the 'census_zipcode_demographics_2022' table. It performs t-SNE 
#              dimensionality reduction to project the data into 2D space and creates 
#              a 2D visualization using Plotly. The visualization shows CBU ZIP codes 
#              in light blue and the 50 most demographically similar non-CBU ZIP codes 
#              in yellow.
#
# Usage: Execute this script to generate the 2D t-SNE plot. Ensure the environment
#        variables for MySQL connection are properly set in '.env.local'. The Plotly
#        visualization will open in the browser.
# --------------------------------------------------------------------------------


import json
import numpy as np
import plotly.graph_objs as go
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import euclidean_distances
from sqlalchemy import create_engine
import pandas as pd
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import os

# Load environment variables for MySQL connection
load_dotenv('.env.local')

# MySQL credentials
host = os.getenv('AZURE_MYSQL_HOST')
user = os.getenv('AZURE_MYSQL_USERNAME')
password = os.getenv('AZURE_MYSQL_PASSWORD')
db_name = 'navalx'

# Create the MySQL engine connection
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')

# Query to retrieve data from the MySQL table
query = """
    SELECT Zip_Code, 
           Population, 
           Median_Income, 
           Bachelor_Degree, 
           Graduate_Professional_Degree, 
           White_Alone, 
           Black_Alone, 
           Hispanic_Latino, 
           Unemployment, 
           Median_Home_Value
    FROM census_zipcode_demographics_2022
"""

# Load data from the MySQL table
full_census_data = pd.read_sql(query, engine)

# Ensure Zip_Code is treated as a string and remove leading/trailing spaces
full_census_data['Zip_Code'] = full_census_data['Zip_Code'].astype(str).str.strip()

# Replace NULL (NaN) values with 0 or the median, depending on the column's type
full_census_data.fillna({
    'Population': 0,  # No population = 0
    'Median_Income': full_census_data['Median_Income'].median(),  # Replace with median income
    'Bachelor_Degree': 0,  # No bachelor degrees = 0
    'Graduate_Professional_Degree': 0,  # No graduate degrees = 0
    'White_Alone': 0,  # No white population = 0
    'Black_Alone': 0,  # No black population = 0
    'Hispanic_Latino': 0,  # No Hispanic population = 0
    'Unemployment': full_census_data['Unemployment'].median(),  # Replace with median unemployment
    'Median_Home_Value': full_census_data['Median_Home_Value'].median()  # Replace with median home value
}, inplace=True)

# List of CBU student zip codes
cbu_zipcodes = ['92503', '92504', '92508', '92506', '92880', '92571', '92336', '92509', 
                '92882', '92399', '92881', '92505', '92223', '92557', '92553']

# Filter the census data for CBU zip codes
cbu_census_data = full_census_data[full_census_data['Zip_Code'].isin(cbu_zipcodes)]

# Check if the filtered data is empty
if cbu_census_data.empty:
    print("No CBU zip codes found in the dataset. Please check the Zip_Code format.")
    print("CBU Zip Codes provided:", cbu_zipcodes)
    print("Sample Zip Codes from dataset:", full_census_data['Zip_Code'].unique())
else:
    # Proceed with the rest of the code
    print("Found CBU Zip Codes:", cbu_census_data['Zip_Code'].unique())
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

    # Perform t-SNE to reduce the data to 2D for both datasets
    tsne = TSNE(n_components=2, random_state=42, perplexity=5, init='random')

    # Combine the data before applying t-SNE
    combined_data_scaled = np.vstack([cbu_census_data_scaled, top_50_non_cbu_census_data_scaled])
    combined_coords = tsne.fit_transform(combined_data_scaled)

    # Extract CBU and top 50 non-CBU coordinates
    cbu_coords = combined_coords[:len(cbu_census_data)]
    non_cbu_coords = combined_coords[len(cbu_census_data):]

    # Extract demographic information for hover for both CBU and non-CBU zip codes
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

    # Prepare the 2D plot with CBU zip codes in light blue and top 50 non-CBU zip codes in yellow
    trace_cbu = go.Scatter(
        x=cbu_coords[:, 0],
        y=cbu_coords[:, 1],
        mode='markers+text',
        marker=dict(
            size=12,
            color='lightblue',  # Set CBU zip codes to light blue
            opacity=0.8
        ),
        text=cbu_census_data['Zip_Code'],  # Display ZIP codes on hover
        hoverinfo='text',
        hovertext=cbu_hover_info  # Attach the demographic info to each point
    )

    trace_non_cbu = go.Scatter(
        x=non_cbu_coords[:, 0],
        y=non_cbu_coords[:, 1],
        mode='markers+text',
        marker=dict(
            size=12,
            color='yellow',  # Set non-CBU zip codes to yellow
            opacity=0.8
        ),
        text=top_50_non_cbu_census_data['Zip_Code'],  # Display ZIP codes on hover
        hoverinfo='text',
        hovertext=non_cbu_hover_info  # Attach the demographic info to each point
    )

    layout = go.Layout(
        title='2D t-SNE Map of ZIP Codes Based on Demographics',
        xaxis=dict(title='t-SNE Dimension 1'),
        yaxis=dict(title='t-SNE Dimension 2'),
        margin=dict(l=0, r=0, b=0, t=40),
        autosize=True,
        height=None,  # Set to None to allow dynamic height
        width=None    # Set to None to allow dynamic width
    )

    fig = go.Figure(data=[trace_cbu, trace_non_cbu], layout=layout)

    # Show the 2D plot
    fig.show()
