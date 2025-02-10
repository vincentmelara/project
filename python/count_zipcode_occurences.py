# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    count_zipcode_occurrences.py
# Date Created: 2024-09-13
#
# Description: This script reads enrollment data from a dataset, counts the 
#              occurrences of each ZIP code, and saves the result into a CSV file.
#
# Usage: Run this script to generate a CSV file containing each ZIP code and 
#        the number of occurrences in the enrollment dataset.
# --------------------------------------------------------------------------------

import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# MySQL credentials
host = os.getenv('AZURE_MYSQL_HOST')
user = os.getenv('AZURE_MYSQL_USERNAME')
password = os.getenv('AZURE_MYSQL_PASSWORD')
db_name = 'navalx'

# Connect to MySQL and retrieve enrollment data
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
enrollment_query = "SELECT Mailing_Zip_Postal_Code FROM enrollment_2019_2023"
enrollment_data = pd.read_sql(enrollment_query, engine)

# Count the occurrences of each ZIP code
zip_code_counts = enrollment_data['Mailing_Zip_Postal_Code'].value_counts().reset_index()
zip_code_counts.columns = ['Zip_Code', 'Count']

# Save the result to a CSV file
output_file = 'zipcode_occurrences.csv'
zip_code_counts.to_csv(output_file, index=False)

print(f"Data successfully saved to {output_file}")
