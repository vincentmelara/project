# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    cluster_5_similiar_zipcodes.py
# Date Created: 2024-09-12
#
# Description: This script processes ZIP code demographic data to identify the most 
#              demographically similar ZIP codes using cosine similarity. The script 
#              clusters ZIP codes using KMeans based on population, income, education, 
#              and other factors, and finds the top 5 most similar ZIP codes for each 
#              one in the dataset. The results are saved as a JSON file for further 
#              visualization and analysis.
#
# Usage: Run this script to analyze ZIP code similarities and generate 'zip_code_similarities.json' 
#        containing the most similar ZIP codes for each ZIP code in the dataset.
# --------------------------------------------------------------------------------

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.impute import SimpleImputer
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

# Retrieve enrollment data
enrollment_query = "SELECT Mailing_Zip_Postal_Code FROM enrollment_2019_2023"
enrollment_data = pd.read_sql(enrollment_query, engine)

# 1. Count the occurrences of each ZIP code in the enrollment dataset
zip_code_counts = enrollment_data['Mailing_Zip_Postal_Code'].value_counts().reset_index()
zip_code_counts.columns = ['Zip_Code', 'Count']
print("Top ZIP Codes by number of students:")
print(zip_code_counts.head(10))  # Print top 10 zip codes

# Relevant features for clustering (adjusted based on schema)
features = ['Population', 'Median_Income', 'Bachelor_Degree', 'Graduate_Professional_Degree', 
            'White_Alone', 'Black_Alone', 'Hispanic_Latino', 'Unemployment', 'Median_Home_Value']

# Impute missing values with the mean for each feature
imputer = SimpleImputer(strategy='mean')
census_data_imputed = imputer.fit_transform(census_data[features])

# Standardize the data for clustering after imputation
scaler = StandardScaler()
census_data_scaled = scaler.fit_transform(census_data_imputed)

# Perform KMeans clustering
kmeans = KMeans(n_clusters=5, random_state=0)
census_data['Cluster'] = kmeans.fit_predict(census_data_scaled)

# 2. Merge census clusters with the enrollment data based on ZIP codes
merged_data = pd.merge(zip_code_counts, census_data[['Zip_Code', 'Cluster'] + features], on='Zip_Code', how='left')

# Initialize a list to hold the output for saving to JSON
output_data = []

# 3. Find the top 5 most demographically similar ZIP codes using cosine similarity
for index, row in merged_data.iterrows():
    zip_output = {
        "zip_code": row['Zip_Code'],
        "count": row['Count'],
        "similar_zips": []
    }
    
    # Check if the ZIP code exists in the census data
    if row['Zip_Code'] not in census_data['Zip_Code'].values:
        print(f"ZIP Code {row['Zip_Code']} not found in census data. Skipping.")
        continue
    
    # Get the index of the current ZIP code
    current_zip_index = census_data[census_data['Zip_Code'] == row['Zip_Code']].index[0]
    current_zip_features = census_data_scaled[current_zip_index].reshape(1, -1)
    all_other_zips_features = census_data_scaled[census_data['Zip_Code'] != row['Zip_Code']]
    
    # Calculate cosine similarity between current ZIP and all others
    similarities = cosine_similarity(current_zip_features, all_other_zips_features).flatten()
    
    # Filter out negative similarities
    positive_similarities = [(i, sim) for i, sim in enumerate(similarities) if sim > 0]

    # Sort based on similarity scores (highest to lowest)
    positive_similarities = sorted(positive_similarities, key=lambda x: x[1], reverse=True)

    # Select top 5 or fewer, depending on available positive similarities
    top_similarities = positive_similarities[:5] if len(positive_similarities) >= 5 else positive_similarities

    # Get the actual rows from census_data corresponding to the top similarity indices
    top_5_indices = [sim[0] for sim in top_similarities]
    similar_zips = census_data[census_data['Zip_Code'] != row['Zip_Code']].iloc[top_5_indices]

    print(f"\nTop {len(top_similarities)} similar ZIP codes for {row['Zip_Code']} (Appears {row['Count']} times):")
    
    # Append the details of similar ZIP codes
    for i, (index_sim, similarity_score) in enumerate(top_similarities):
        similar_zip_row = similar_zips.iloc[i]
        zip_output['similar_zips'].append({
            "zip_code": str(similar_zip_row['Zip_Code']),
            "population": int(similar_zip_row['Population']) if not pd.isna(similar_zip_row['Population']) else None,
            "median_income": int(similar_zip_row['Median_Income']) if not pd.isna(similar_zip_row['Median_Income']) else None,
            "cluster": int(similar_zip_row['Cluster']),
            "similarity": round(float(similarity_score), 4)
        })
        print(f"{similar_zip_row['Zip_Code']} - Population: {similar_zip_row['Population']}, "
            f"Median Income: {similar_zip_row['Median_Income']}, Cluster: {similar_zip_row['Cluster']} "
            f"(Similarity: {similarity_score:.4f})")

    
    # Append the processed ZIP code output to the list
    output_data.append(zip_output)

# Save the output data to a JSON file
output_file = "zip_code_similarities.json"
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=4)

print(f"\nData successfully saved to {output_file}")
