# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    get_city_census_data.py
# Date Created: 2024-09-11
#
# Description: This script fetches multiple demographic variables for all places 
#              (cities) from the U.S. Census Bureau API. It retrieves city-level 
#              population, median income, median age, education, racial demographics,
#              and other relevant metrics, converts the data into a pandas DataFrame,
#              and saves it as a CSV file.
#
# Usage: Run this script to fetch data for all cities and save it to 
#        'census_city_demographics_2022.csv'. Ensure the Census API key is set.
# --------------------------------------------------------------------------------

import requests
import pandas as pd

# Your Census API key
api_key = 'e3dbe9a58303660e8873f4a59a1661f17f9c106f'

# URL to fetch multiple demographic variables for all places (cities)
url = f'https://api.census.gov/data/2022/acs/acs5?get=NAME,B01003_001E,B19013_001E,B01002_001E,B15003_017E,B15003_001E,B15003_021E,B02001_002E,B02001_003E,B03002_003E,B23025_001E,B23025_005E,B27001_001E,B27001_005E,B17001_001E,B17001_002E,B25077_001E,B25064_001E,B25003_002E,B25003_003E,B16001_002E,B08013_001E,B12001_001E,B12001_003E&for=place:*&in=state:*&key={api_key}'

# Make the request to the Census API
response = requests.get(url)

# Convert response to JSON format
data = response.json()

# Load the data into a pandas DataFrame
columns = data[0]  # First element contains the column names
rows = data[1:]    # Remaining elements contain the data

# Create DataFrame from the rows and columns
df = pd.DataFrame(rows, columns=columns)

# Rename columns for better clarity (added State for the extra column)
df.columns = [
    'City', 
    'Population', 
    'Median_Income', 
    'Median_Age', 
    'Bachelor_Degree', 
    'Total_Education_Population', 
    'Graduate_Professional_Degree', 
    'White_Alone', 
    'Black_Alone', 
    'Hispanic_Latino', 
    'Employment_Status', 
    'Unemployment', 
    'Total_Health_Insurance_Coverage', 
    'Without_Health_Insurance', 
    'Total_Pop_Poverty_Status', 
    'Below_Poverty_Level', 
    'Median_Home_Value', 
    'Median_Gross_Rent', 
    'Owner_Occupied_Units', 
    'Renter_Occupied_Units', 
    'Non_English_Speakers', 
    'Means_of_Transportation_to_Work', 
    'Total_Pop_Marital_Status', 
    'Married_Population', 
    'State_Code',    # Add this to account for the extra column
    'Place_Code'
]

# Convert relevant columns to numeric types for proper analysis
df['Population'] = pd.to_numeric(df['Population'], errors='coerce')
df['Median_Income'] = pd.to_numeric(df['Median_Income'], errors='coerce')
df['Median_Age'] = pd.to_numeric(df['Median_Age'], errors='coerce')
df['Bachelor_Degree'] = pd.to_numeric(df['Bachelor_Degree'], errors='coerce')
df['Total_Education_Population'] = pd.to_numeric(df['Total_Education_Population'], errors='coerce')
df['Graduate_Professional_Degree'] = pd.to_numeric(df['Graduate_Professional_Degree'], errors='coerce')
df['White_Alone'] = pd.to_numeric(df['White_Alone'], errors='coerce')
df['Black_Alone'] = pd.to_numeric(df['Black_Alone'], errors='coerce')
df['Hispanic_Latino'] = pd.to_numeric(df['Hispanic_Latino'], errors='coerce')
df['Employment_Status'] = pd.to_numeric(df['Employment_Status'], errors='coerce')
df['Unemployment'] = pd.to_numeric(df['Unemployment'], errors='coerce')
df['Total_Health_Insurance_Coverage'] = pd.to_numeric(df['Total_Health_Insurance_Coverage'], errors='coerce')
df['Without_Health_Insurance'] = pd.to_numeric(df['Without_Health_Insurance'], errors='coerce')
df['Total_Pop_Poverty_Status'] = pd.to_numeric(df['Total_Pop_Poverty_Status'], errors='coerce')
df['Below_Poverty_Level'] = pd.to_numeric(df['Below_Poverty_Level'], errors='coerce')
df['Median_Home_Value'] = pd.to_numeric(df['Median_Home_Value'], errors='coerce')
df['Median_Gross_Rent'] = pd.to_numeric(df['Median_Gross_Rent'], errors='coerce')
df['Owner_Occupied_Units'] = pd.to_numeric(df['Owner_Occupied_Units'], errors='coerce')
df['Renter_Occupied_Units'] = pd.to_numeric(df['Renter_Occupied_Units'], errors='coerce')
df['Non_English_Speakers'] = pd.to_numeric(df['Non_English_Speakers'], errors='coerce')
df['Means_of_Transportation_to_Work'] = pd.to_numeric(df['Means_of_Transportation_to_Work'], errors='coerce')
df['Total_Pop_Marital_Status'] = pd.to_numeric(df['Total_Pop_Marital_Status'], errors='coerce')
df['Married_Population'] = pd.to_numeric(df['Married_Population'], errors='coerce')

# Display the first few rows of the DataFrame
print(df.head())

# Save the DataFrame to a CSV file
df.to_csv('census_city_demographics_2022.csv', index=False)
