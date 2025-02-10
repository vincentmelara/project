# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    split_city_state_mysql.py
# Date Created: 2024-09-13
#
# Description: This script retrieves data from the 'census_city_demographics_2022' table
#              in a MySQL database. It processes the 'City' column by splitting it into
#              separate 'City' and 'State' columns, removes any commas from city names, 
#              and maps full state names to their respective two-letter abbreviations. 
#              The updated data is then written back to the MySQL table.
#
# Usage: Ensure the environment variables for MySQL connection are set in '.env.local'.
#        Run this script to update the 'census_city_demographics_2022' table in MySQL 
#        with the modified 'City' and 'State' data.
# --------------------------------------------------------------------------------


import pandas as pd
import pymysql
import logging
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Set up logging
logger = logging.getLogger('city_state_split')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Load environment variables from .env.local file
load_dotenv('.env.local')

# Get MySQL credentials from environment variables
host = os.getenv('AZURE_MYSQL_HOST')
user = os.getenv('AZURE_MYSQL_USERNAME')
password = os.getenv('AZURE_MYSQL_PASSWORD')
db_name = 'navalx'

# Create SQLAlchemy engine to connect to MySQL
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')

# Dictionary mapping state names to their two-letter abbreviations
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Fetch data from MySQL table
logger.info("Fetching data from MySQL table census_city_demographics_2022")
df = pd.read_sql('SELECT * FROM census_city_demographics_2022', con=engine)

# Splitting the 'City' column into 'City' and 'State'
logger.info("Splitting City column into City and State")
df[['City', 'State']] = df['City'].str.rsplit(' ', n=1, expand=True)

# Trim any commas in the 'City' column
logger.info("Trimming commas from the City column")
df['City'] = df['City'].str.replace(',', '', regex=False)

# Map full state names to abbreviations
logger.info("Mapping full state names to abbreviations")
df['State'] = df['State'].replace(state_abbrev)

# Move the 'State' column to be right after the 'City' column
columns = list(df.columns)
city_index = columns.index('City')
columns.insert(city_index + 1, columns.pop(columns.index('State')))
df = df[columns]  # Reorder the DataFrame

# Log the results
logger.info(f"Updated dataframe:\n{df.head()}")

# Write the modified DataFrame back to the MySQL table
logger.info("Writing updated data back to MySQL table")
df.to_sql('census_city_demographics_2022', con=engine, if_exists='replace', index=False)

logger.info("City and state abbreviation process complete, and data updated in MySQL")
