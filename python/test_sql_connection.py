# --------------------------------------------------------------------------------
# Author:       Tim Allec
# File name:    test_sql_connection.py
# Date Created: 2024-09-11
#
# Description: This script tests a connection to a MySQL database using environment 
#              variables for host, username, and password. It logs the connection 
#              attempt and performs a simple query to verify the connection. 
#              The script includes error handling and ensures the connection 
#              is closed after use.
#
# Usage: Update the database name and ensure the environment variables are correctly 
#        set in your .env.local file. Run the script to verify the connection.
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


def get_connection(db):
    """Establish a secure connection to the MySQL database using environment variables."""
    host = os.getenv('AZURE_MYSQL_HOST')
    user = os.getenv('AZURE_MYSQL_USERNAME')
    password = os.getenv('AZURE_MYSQL_PASSWORD')

    # Log the connection details for debugging (without sensitive information)
    logger.debug(f"Attempting connection to MySQL database at {host} with user {user}")

    if not host or not user or not password:
        logger.error("Database connection information is missing. Please check your .env file.")
        sys.exit(1)

    try:
        # Attempt to connect to the database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Successfully connected to the database")
        return connection
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to the database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example database name (replace 'navalx' with your actual database name)
    db_name = 'navalx'

    # Test the database connection
    connection = get_connection(db_name)

    try:
        # Perform a simple query to verify connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db_selected = cursor.fetchone()
            logger.info(f"Successfully connected to database: {db_selected['DATABASE()']}")

    finally:
        # Close the connection when done
        if connection and connection.open:
            connection.close()
            logger.info("Database connection closed")
