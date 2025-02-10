# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    cluster_all_zipcodes.py
# Date Created: 2024-09-13
#
# Description: This script connects to a MySQL database to retrieve demographic data 
#              from the 'census_zipcode_demographics_2022' table. It standardizes 
#              the data and performs KMeans clustering on ZIP code demographics. The 
#              resulting clusters are then saved, along with demographic data, into a 
#              JSON file. Each ZIP code is assigned a cluster based on its demographic 
#              similarity to others.
#
# Usage: Execute this script to cluster ZIP codes and save the output to a JSON file. 
#        Ensure the environment variables for MySQL connection are set in '.env.local'. 
#        The JSON file 'zipcode_demographic_data.json' will contain the processed output.
# --------------------------------------------------------------------------------


import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('.env.local')

# MySQL credentials
host = os.getenv('AZURE_MYSQL_HOST')
user = os.getenv('AZURE_MYSQL_USERNAME')
password = os.getenv('AZURE_MYSQL_PASSWORD')
db_name = 'navalx'

# Connect to MySQL and retrieve census data
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
census_query = "SELECT * FROM census_zipcode_demographics_2022"
census_data = pd.read_sql(census_query, engine)

# Relevant features for clustering (adjusted based on schema)
features = ['Population', 'Median_Income', 'Bachelor_Degree', 'Graduate_Professional_Degree', 
            'White_Alone', 'Black_Alone', 'Hispanic_Latino', 'Unemployment', 'Median_Home_Value']

# Standardize the data for clustering
scaler = StandardScaler()
census_data_scaled = scaler.fit_transform(census_data[features])

# Perform KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=0)
census_data['Cluster'] = kmeans.fit_predict(census_data_scaled)

# Initialize a list to hold the output for saving to JSON
output_data = []

# Process each ZIP code and its demographics
for index, row in census_data.iterrows():
    zip_output = {
        "zip_code": row['Zip_Code'],
        "population": row['Population'],
        "median_income": row['Median_Income'],
        "cluster": int(row['Cluster'])  # No need for enrollment flag anymore
    }
    
    # Append the processed ZIP code output to the list
    output_data.append(zip_output)

# Save the output data to a JSON file
output_file = "zipcode_demographic_data.json"
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=4)

print(f"\nData successfully saved to {output_file}")
