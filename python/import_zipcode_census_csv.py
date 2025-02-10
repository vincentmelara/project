# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    import_csv_to_mysql.py
# Date Created: 2024-09-11
#
# Description: This script imports ZIP code level census demographic data from a CSV 
#              file ('census_zipcode_demographics_full_extended_2022.csv') into a 
#              MySQL database table named 'census_zipcode_demographics_2022'. 
#              The script handles table creation, data insertion, and renaming of 
#              columns to make them MySQL-friendly. If the table already exists, 
#              data insertion is skipped, and an error is logged.
#
# Usage: Ensure the CSV file path and MySQL credentials are correctly set. The table 
#        will be created if it does not already exist.
# --------------------------------------------------------------------------------

import pandas as pd
import pymysql
import sys
import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger('import_csv_to_mysql.py')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Load environment variables from .env.local file if it exists
APP_ROOT = os.path.join(os.path.dirname(__file__))
local_dotenv_path = os.path.join(APP_ROOT, '../.env.local')

if os.path.exists(local_dotenv_path):
    load_dotenv(local_dotenv_path, override=True)
    logger.debug(f"Loaded environment variables from {local_dotenv_path}")
else:
    load_dotenv()
    logger.debug("Loaded environment variables from the default .env file")

# CSV file path (updated for your local path)
csv_file_path = r'C:\Users\User\Downloads\census_zipcode_demographics_full_extended_2022.csv'
table_name = 'census_zipcode_demographics_2022'

def get_connection(db):
    """Establish a secure connection to the MySQL database using environment variables."""
    host = os.getenv('AZURE_MYSQL_HOST')
    user = os.getenv('AZURE_MYSQL_USERNAME')
    password = os.getenv('AZURE_MYSQL_PASSWORD')

    if not host or not user or not password:
        logger.error("Database connection information is missing. Please check your .env file.")
        sys.exit(1)

    return pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)

def check_table_exists(cursor, table_name):
    """Checks if the table already exists in the database."""
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

def create_table_from_csv(cursor, table_name):
    """Creates a table based on the CSV file columns and data types."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Name VARCHAR(255),
        Population INT,
        Median_Income INT,
        Median_Age FLOAT,
        Bachelor_Degree INT,
        Total_Education_Population INT,
        Graduate_Professional_Degree INT,
        White_Alone INT,
        Black_Alone INT,
        Hispanic_Latino INT,
        Employment_Status INT,
        Unemployment INT,
        Total_Health_Insurance_Coverage INT,
        Without_Health_Insurance INT,
        Total_Pop_Poverty_Status INT,
        Below_Poverty_Level INT,
        Median_Home_Value INT,
        Median_Gross_Rent INT,
        Owner_Occupied_Units INT,
        Renter_Occupied_Units INT,
        Non_English_Speakers INT,
        Means_of_Transportation_to_Work INT,
        Total_Pop_Marital_Status INT,
        Married_Population INT,
        ZCTA VARCHAR(10)
    );
    """
    cursor.execute(create_table_query)
    logger.info(f"Table `{table_name}` created successfully.")

def insert_csv_data_to_table(connection, df, table_name):
    """Inserts CSV data into the newly created table."""
    cursor = connection.cursor()

    # Prepare the INSERT INTO query
    columns = ', '.join(df.columns)
    values_placeholder = ', '.join(['%s'] * len(df.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder})"

    # Convert DataFrame to list of tuples, replacing NaN with None
    data = [tuple(None if pd.isna(value) else value for value in row) for row in df.to_numpy()]

    try:
        cursor.executemany(insert_query, data)
        connection.commit()
        logger.info(f"Inserted {cursor.rowcount} rows into `{table_name}`.")
    except Exception as e:
        connection.rollback()
        logger.error(f"Failed to insert data into MySQL table: {e}")
    finally:
        cursor.close()

def main():
    # Read CSV file into pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Rename columns to be MySQL-friendly (replace spaces and special characters with underscores)
    df.columns = df.columns.str.replace(' ', '_').str.replace('/', '_')

    # Replace NaN with None for MySQL compatibility
    df = df.where(pd.notnull(df), None)

    # Establish MySQL connection
    connection = get_connection('navalx')
    cursor = connection.cursor()

    try:
        # Check if the table already exists
        if check_table_exists(cursor, table_name):
            logger.error(f"Table `{table_name}` already exists. Data insertion skipped.")
        else:
            # Create a new table based on the CSV file columns
            create_table_from_csv(cursor, table_name)

            # Insert CSV data into the new table
            insert_csv_data_to_table(connection, df, table_name)
    finally:
        # Close the connection
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
