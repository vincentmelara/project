# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    export_to_csv.py
# Date Created: 2024-09-18
#
# Description: This script turns the census_zipcode_demographics_2022 table into a CSV file
# Usage: Run to export data from census_zipcode_demographics_2022 to a CSV file.
# -----------------------------------------------------------------------------


import sys
import os
import pymysql
import csv
import logging
import time
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger('export_to_csv.py')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Load environment variables from .env.local file if it exists
APP_ROOT = os.path.join(os.path.dirname(__file__))
local_dotenv_path = os.path.join(APP_ROOT, '.env.local')

if os.path.exists(local_dotenv_path):
    load_dotenv(local_dotenv_path, override=True)
    logger.debug(f"Loaded environment variables from {local_dotenv_path}")
else:
    load_dotenv()
    logger.debug("Loaded environment variables from the default .env file")

def get_connection(db):
    """Establish a secure connection to the MySQL database using environment variables"""
    host = os.getenv('AZURE_MYSQL_HOST')
    user = os.getenv('AZURE_MYSQL_USERNAME')
    password = os.getenv('AZURE_MYSQL_PASSWORD')

    if not host or not user or not password:
        logger.error("Database connection information is missing. Please check your .env file.")
        sys.exit(1)

    return pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)

def export_to_csv(db, output_file, batch_size=1000):
    start_time = time.time()

    try:
        # Connect to the database
        connection = get_connection(db)
        cursor = connection.cursor()

        # Query to get the total number of rows
        cursor.execute("SELECT COUNT(*) AS total FROM census_zipcode_demographics_2022")
        total_rows = cursor.fetchone()['total']
        logger.info(f"Total rows to export: {total_rows}")

        # Open CSV file for writing
        with open(output_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row
            header = [
                'my_row_id', 'Zip_Code', 'Population', 'Median_Income', 'Median_Age', 
                'Bachelor_Degree', 'Total_Education_Population', 'Graduate_Professional_Degree', 
                'White_Alone', 'Black_Alone', 'Hispanic_Latino', 'Employment_Status', 
                'Unemployment', 'Total_Health_Insurance_Coverage', 'Without_Health_Insurance', 
                'Total_Pop_Poverty_Status', 'Below_Poverty_Level', 'Median_Home_Value', 
                'Median_Gross_Rent', 'Owner_Occupied_Units', 'Renter_Occupied_Units', 
                'Means_of_Transportation_to_Work', 'Total_Pop_Marital_Status', 'Married_Population', 
                'ZCTA'
            ]
            csv_writer.writerow(header)

            # Fetch and process data in batches
            for offset in range(0, total_rows, batch_size):
                query = f"""
                SELECT 
                    my_row_id, Zip_Code, Population, Median_Income, Median_Age, 
                    Bachelor_Degree, Total_Education_Population, Graduate_Professional_Degree, 
                    White_Alone, Black_Alone, Hispanic_Latino, Employment_Status, 
                    Unemployment, Total_Health_Insurance_Coverage, Without_Health_Insurance, 
                    Total_Pop_Poverty_Status, Below_Poverty_Level, Median_Home_Value, 
                    Median_Gross_Rent, Owner_Occupied_Units, Renter_Occupied_Units, 
                    Means_of_Transportation_to_Work, Total_Pop_Marital_Status, 
                    Married_Population, ZCTA
                FROM census_zipcode_demographics_2022
                LIMIT {batch_size} OFFSET {offset};
                """
                cursor.execute(query)
                rows = cursor.fetchall()

                # Write rows to CSV file
                for row in rows:
                    csv_writer.writerow([
                        row['my_row_id'], row['Zip_Code'], row['Population'], row['Median_Income'], row['Median_Age'],
                        row['Bachelor_Degree'], row['Total_Education_Population'], row['Graduate_Professional_Degree'],
                        row['White_Alone'], row['Black_Alone'], row['Hispanic_Latino'], row['Employment_Status'],
                        row['Unemployment'], row['Total_Health_Insurance_Coverage'], row['Without_Health_Insurance'],
                        row['Total_Pop_Poverty_Status'], row['Below_Poverty_Level'], row['Median_Home_Value'],
                        row['Median_Gross_Rent'], row['Owner_Occupied_Units'], row['Renter_Occupied_Units'],
                        row['Means_of_Transportation_to_Work'], row['Total_Pop_Marital_Status'], row['Married_Population'],
                        row['ZCTA']
                    ])
                logger.info(f"Processed {offset + len(rows)} / {total_rows} rows")

        # Close the cursor and connection
        cursor.close()
        connection.close()

        end_time = time.time()
        logger.info(f"Data has been exported to {output_file}")
        logger.info(f"Export completed in {end_time - start_time:.2f} seconds")

    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to MySQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    database_name = 'navalx'  # Replace with your actual database name
    output_file_path = 'census_zipcode_demographics_2022.csv'  # Path to the output CSV file

    export_to_csv(database_name, output_file_path)
