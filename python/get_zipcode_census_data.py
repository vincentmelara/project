# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    get_zipcode_census_data.py
# Date Created: 2024-09-11
#
# Description: This script fetches multiple demographic variables for all ZIP code 
#              tabulation areas (ZCTAs) from the U.S. Census Bureau API. It retrieves 
#              population, median income, education, racial demographics, and other 
#              relevant metrics, converts the data into a pandas DataFrame, and saves 
#              it as a CSV file.
#
# Usage: Run this script to fetch data for all ZIP code areas and save it to 
#        'census_zipcode_demographics_2022.csv'. Ensure the Census API key is set.
# --------------------------------------------------------------------------------

import requests
import pandas as pd

# Your Census API key
api_key = 'e3dbe9a58303660e8873f4a59a1661f17f9c106f'

# URL to fetch multiple demographic variables for all ZIP code tabulation areas
url = f'https://api.census.gov/data/2022/acs/acs5?get=NAME,B01003_001E,B19013_001E,B01002_001E,B15003_017E,B15003_001E,B15003_021E,B02001_002E,B02001_003E,B03002_003E,B23025_001E,B23025_005E,B27001_001E,B27001_005E,B17001_001E,B17001_002E,B25077_001E,B25064_001E,B25003_002E,B25003_003E,B16001_002E,B08013_001E,B12001_001E,B12001_003E&for=zip%20code%20tabulation%20area:*&key={api_key}'

# Make the request
response = requests.get(url)

# Convert response to JSON format
data = response.json()

# Load the data into a pandas DataFrame
columns = data[0]  # First element contains the column names
rows = data[1:]    # Remaining elements contain the data

# Create DataFrame from the rows and columns
df = pd.DataFrame(rows, columns=columns)

# Rename columns for better clarity
df.columns = [
    'Name', 
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
    'ZCTA'
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
df.to_csv('census_zipcode_demographics_2022.csv', index=False)

# Name:

# The official name for the ZIP Code Tabulation Area (ZCTA). It usually follows the format “ZCTA5 XXXXX,” where XXXXX is the ZIP code.
# Population (B01003_001E):

# Total population in the ZCTA (ZIP Code Tabulation Area). This represents the entire population living in that ZIP code region.
# Median_Income (B19013_001E):

# Median household income in the ZCTA. It represents the middle income when households in the ZIP code are ranked from lowest to highest.
# Median_Age (B01002_001E):

# The median age of the population in the ZCTA. This is the age that divides the population into two halves: half are younger, and half are older than the median age.
# Bachelor_Degree (B15003_017E):

# The total number of people aged 25 and over in the ZCTA who have attained a bachelor's degree. This gives an indication of the education level of the population.
# Total_Education_Population (B15003_001E):

# The total population aged 25 years and older for whom educational attainment is measured. This is the base population for calculating education-related metrics.
# Graduate_Professional_Degree (B15003_021E):

# The total number of people aged 25 and over in the ZCTA who have attained a graduate or professional degree (e.g., master's, doctorate, or professional degrees like law or medicine).
# White_Alone (B02001_002E):

# The population in the ZCTA identifying as "White alone." This means they are racially categorized as White and do not identify as part of another racial group.
# Black_Alone (B02001_003E):

# The population in the ZCTA identifying as "Black or African American alone." This means they are racially categorized as Black and do not identify as part of another racial group.
# Hispanic_Latino (B03002_003E):

# The population in the ZCTA identifying as Hispanic or Latino, regardless of race. This reflects ethnic diversity rather than racial diversity.
# Employment_Status (B23025_001E):

# Total population aged 16 years and over who are considered in the labor force (both employed and unemployed). This includes anyone who is working or actively seeking work.
# Unemployment (B23025_005E):

# The number of unemployed people within the ZCTA. These are individuals who are not currently working but are actively seeking employment.
# Total_Health_Insurance_Coverage (B27001_001E):

# Total population in the ZCTA who have health insurance coverage.
# Without_Health_Insurance (B27001_005E):

# The total number of people in the ZCTA who are not covered by health insurance.
# Total_Pop_Poverty_Status (B17001_001E):

# The total population in the ZCTA for whom poverty status is determined. This is the base population used to calculate poverty statistics.
# Below_Poverty_Level (B17001_002E):

# The population in the ZCTA who are living below the poverty level. The poverty level is determined based on income thresholds set by the U.S. government.
# Median_Home_Value (B25077_001E):

# The median value of owner-occupied homes in the ZCTA. This represents the midpoint value when homes are ranked from least to most expensive.
# Median_Gross_Rent (B25064_001E):

# The median rent paid by renters in the ZCTA. This includes rent and utilities.
# Owner_Occupied_Units (B25003_002E):

# The number of housing units in the ZCTA that are occupied by the owner (i.e., where the occupant owns the home they live in).
# Renter_Occupied_Units (B25003_003E):

# The number of housing units in the ZCTA that are occupied by renters (i.e., where the occupant rents the home they live in).
# Non_English_Speakers (B16001_002E):

# The population aged 5 years and over in the ZCTA who speak a language other than English at home. This gives insight into the linguistic diversity of the area.
# Means_of_Transportation_to_Work (B08013_001E):

# The total number of people in the ZCTA who use a specific means of transportation to commute to work (e.g., driving, public transportation, walking).
# Total_Pop_Marital_Status (B12001_001E):

# The total population aged 15 years and older for whom marital status is determined. This includes both married and unmarried individuals.
# Married_Population (B12001_003E):

# The number of people aged 15 years and older in the ZCTA who are currently married.
# ZCTA:

# The ZIP Code Tabulation Area (ZCTA) associated with the data. ZCTAs are generalized representations of ZIP codes used by the Census Bureau to tabulate data.