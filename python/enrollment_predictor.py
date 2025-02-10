# backend/enrollment_predictor.py

import os
from pathlib import Path
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Growth Calculation Functions
def calculate_cagr(start_value, end_value, periods):
    if periods <= 0 or start_value <= 0:
        return np.nan
    return (end_value / start_value) ** (1 / periods) - 1

def calculate_linear_growth(start_value, end_value, periods):
    if periods <= 0:
        return np.nan
    return (end_value - start_value) / periods

# Function to prepare AI context
def prepare_ai_context(combined_data):
    historical_data = [d for d in combined_data if d['type'] == 'historical']
    predicted_data = [d for d in combined_data if d['type'] == 'predicted']

    # Create a summary of historical data
    historical_summary = "Enrollment Data:\n"
    for data in historical_data:
        historical_summary += f"- **{data['year']}**: {data['students']} students\n"

    # Calculate average growth rates
    growth_rates = []
    for i in range(1, len(historical_data)):
        previous = historical_data[i - 1]['students']
        current = historical_data[i]['students']
        growth = (current - previous) / previous
        growth_rates.append(growth)
    average_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
    historical_summary += f"\n**Historical Average Year-over-Year Growth Rate:** {average_growth:.2%}\n"

    # Include demographic data if available
    demographic_summary = "Demographic Information:\n"
    demographic_summary += "- **Average Household Income:** $60,000\n"
    demographic_summary += "- **Population Growth Rate:** 2%\n"
    demographic_summary += "- **Educational Attainment:** 60% Bachelor's Degree\n"
    demographic_summary += "- **Employment Rate:** 95%\n"

    # Current and Previous Year Data
    if len(predicted_data) > 0:
        current_year_data = predicted_data[-1]
    else:
        current_year_data = historical_data[-1]

    if len(historical_data) > 1:
        previous_year_data = historical_data[-2]
    else:
        previous_year_data = historical_data[-1]

    # Construct the prompt
    prompt = (
        f"You are an experienced enrollment analyst for California Baptist University (CBU). Based on the following enrollment data and demographic information, provide a detailed Enrollment Analysis Report for the year 2024.\n\n"
        f"---\n\n"
        f"**Enrollment Data:**\n"
        f"{historical_summary}\n"
        f"**Demographic Information:**\n"
        f"{demographic_summary}\n"
        f"**Comparison:**\n"
        f"Compare the enrollment of {current_year_data['students']} students in {current_year_data['year']} with {previous_year_data['students']} students in {previous_year_data['year']}.\n\n"
        f"**Report Requirements:**\n"
        f"1. **Overview:** Summarize the enrollment changes.\n"
        f"2. **Key Factors Contributing to Enrollment Change:**\n"
        f"   - Introduction of New Programs\n"
        f"   - Economic Stability and Employment\n"
        f"   - Changes in Admission Criteria\n"
        f"   - Population Growth in Surrounding Areas\n"
        f"   - Retention Strategies\n"
        f"3. **Recommendations for Future Enrollment Strategies:**\n"
        f"   - Expand High-Demand Programs\n"
        f"   - Strengthen Community Engagement\n"
        f"   - Enhance Financial Aid and Scholarships\n"
        f"   - Invest in Marketing and Outreach\n"
        f"   - Address Demographic Changes\n"
        f"   - Leverage Alumni Networks\n"
        f"4. **Conclusion:** Provide a summary of findings and future outlook.\n"
    )

    return prompt

# Function to process data and make predictions
def process_enrollment_data():
    # Define the base directory as the directory where this script resides
    base_dir = Path(__file__).parent

    # Load file paths
    enrollment_csv_path = base_dir / '../csvdata/enrollment 2019-2023.csv'
    census_zip_csv_path = base_dir / '../csvdata/census_zipcode_demographics_2022.csv'

    # Verify CSV files exist
    for csv_path in [enrollment_csv_path, census_zip_csv_path]:
        if not csv_path.is_file():
            logger.error("Required CSV file not found: %s", csv_path)
            raise FileNotFoundError(f"Required CSV file not found: {csv_path}")

    # Read CSV files
    try:
        enrollment_df = pd.read_csv(enrollment_csv_path)
        census_zip_df = pd.read_csv(census_zip_csv_path)
        logger.info("CSV files loaded successfully.")
    except Exception as e:
        logger.error("Error reading CSV files: %s", e)
        raise e

    # Clean column names
    enrollment_df.columns = enrollment_df.columns.str.strip()
    census_zip_df.columns = census_zip_df.columns.str.strip()

    # Ensure zip codes are strings and zero-padded
    enrollment_df['Mailing Zip/Postal Code'] = enrollment_df['Mailing Zip/Postal Code'].astype(str).str.zfill(5)
    census_zip_df['Zip_Code'] = census_zip_df['Zip_Code'].astype(str).str.zfill(5)

    # Log enrollment DataFrame columns
    logger.info("Enrollment DataFrame columns:")
    logger.info(enrollment_df.columns.tolist())

    # Log matched zip codes
    matched_zip_codes = enrollment_df['Mailing Zip/Postal Code'].isin(census_zip_df['Zip_Code']).sum()
    total_zip_codes = enrollment_df['Mailing Zip/Postal Code'].nunique()
    logger.info("Matched Zip_Codes: %d out of %d unique zip codes in enrollment data.", matched_zip_codes, total_zip_codes)

    # Merge enrollment data with census_zip_df on Zip_Code
    merged_df = pd.merge(
        enrollment_df,
        census_zip_df,
        how='left',
        left_on='Mailing Zip/Postal Code',
        right_on='Zip_Code',
        suffixes=('_enroll', '_census')
    )

    # Log number of rows after merge
    logger.info("Number of rows after merge: %d", len(merged_df))

    # Log merged_df columns
    logger.info("Columns in merged_df after merge:")
    logger.info(merged_df.columns.tolist())

    # Assign enrollment numbers manually for years 2019-2023
    enrollment_numbers = {
        2019: 11047,
        2020: 11317,
        2021: 11491,
        2022: 11384,
        2023: 11407
    }

    # Extract year from 'Start Term and Year'
    merged_df['year'] = merged_df['Start Term and Year'].astype(str).str.extract(r'(\d{4})').astype(float).astype('Int64')

    # Assign 'students' based on 'year'
    merged_df['students'] = merged_df['year'].map(enrollment_numbers)

    # Filter for years 2019-2023
    merged_df = merged_df[merged_df['year'].isin(enrollment_numbers.keys())]

    # Check for missing demographic data
    demographic_cols = ['Population', 'Bachelor_Degree', 'Graduate_Professional_Degree', 'Median_Income']
    missing_demographics = merged_df[demographic_cols].isnull().any(axis=1)
    num_missing = missing_demographics.sum()
    logger.info("Number of rows with missing demographic data: %d", num_missing)

    if num_missing > 0:
        # Fill missing demographic data with column means if possible
        logger.warning("Filling %d rows with missing demographic data with mean values.", num_missing)
        for col in demographic_cols:
            mean_value = merged_df[col].mean()
            if pd.isnull(mean_value):
                # If mean is NaN (all values are NaN), set a default value, e.g., 0
                logger.warning("Mean value for %s is NaN. Setting default value to 0.", col)
                mean_value = 0
            # Replace the inplace assignment with direct assignment to avoid FutureWarning
            merged_df[col] = merged_df[col].fillna(mean_value)

    # Check if any data remains
    if merged_df.empty:
        logger.error("No data available after handling missing demographic data.")
        raise ValueError("No data available after handling missing demographic data.")

    # Select relevant features
    try:
        merged_df = merged_df[['year', 'students', 'Population', 'Bachelor_Degree', 'Graduate_Professional_Degree', 'Median_Income']]
    except KeyError as e:
        logger.error("Missing columns during selection: %s", e)
        raise e

    # Rename columns for clarity
    merged_df.columns = ['year', 'students', 'population', 'bachelor_degree', 'graduate_degree', 'median_income']

    # Log processed DataFrame
    logger.info("Processed DataFrame for model training:")
    logger.info(merged_df)

    # Calculate growth rates
    merged_df = merged_df.sort_values('year').reset_index(drop=True)

    # Calculate year-over-year growth rates
    merged_df['pop_growth'] = merged_df['population'].pct_change()
    merged_df['bachelor_growth'] = merged_df['bachelor_degree'].pct_change()
    merged_df['graduate_growth'] = merged_df['graduate_degree'].pct_change()
    merged_df['income_growth'] = merged_df['median_income'].pct_change()

    # Log growth rates
    logger.info("Calculated Growth Rates (Year-over-Year % Change):")
    logger.info(merged_df[['year', 'pop_growth', 'bachelor_growth', 'graduate_growth', 'income_growth']])

    # Drop the first row with NaN growth rates
    merged_df = merged_df.dropna(subset=['pop_growth', 'bachelor_growth', 'graduate_growth', 'income_growth', 'students'])

    # Check if data remains
    if merged_df.empty:
        logger.error("No data available after dropping rows with NaN growth rates.")
        raise ValueError("No data available after dropping rows with NaN growth rates.")

    # Use the last year's growth rates to predict 2024 demographics
    last_row = merged_df.iloc[-1]
    last_year = last_row['year']
    last_population = last_row['population']
    last_bachelor_degree = last_row['bachelor_degree']
    last_graduate_degree = last_row['graduate_degree']
    last_median_income = last_row['median_income']

    last_pop_growth = last_row['pop_growth']
    last_bachelor_growth = last_row['bachelor_growth']
    last_graduate_growth = last_row['graduate_growth']
    last_income_growth = last_row['income_growth']

    # Check if growth rates are not NaN
    if pd.isnull(last_pop_growth) or pd.isnull(last_bachelor_growth) or pd.isnull(last_graduate_growth) or pd.isnull(last_income_growth):
        logger.error("Growth rates contain NaN values.")
        raise ValueError("Growth rates contain NaN values.")

    # Predict demographics for 2024
    predicted_population = last_population * (1 + last_pop_growth)
    predicted_bachelor_degree = last_bachelor_degree * (1 + last_bachelor_growth)
    predicted_graduate_degree = last_graduate_degree * (1 + last_graduate_growth)
    predicted_median_income = last_median_income * (1 + last_income_growth)

    # Prepare prediction data
    prediction_year = 2024
    prediction_data = pd.DataFrame({
        'year': [prediction_year],
        'population': [predicted_population],
        'bachelor_degree': [predicted_bachelor_degree],
        'graduate_degree': [predicted_graduate_degree],
        'median_income': [predicted_median_income]
    })

    logger.info("Predicted Demographic Data for 2024:\n%s", prediction_data)

    # Fit Linear Regression model
    X = merged_df[['year', 'population', 'bachelor_degree', 'graduate_degree', 'median_income']]
    y = merged_df['students']

    # Check for NaN in X and y
    if X.isnull().any().any() or y.isnull().any():
        logger.error("Input X or y contains NaN values.")
        raise ValueError("Input X or y contains NaN values.")

    model = LinearRegression()
    model.fit(X, y)
    logger.info("Linear Regression model trained successfully.")

    # Predict enrollment for 2024
    future_enrollment = model.predict(
        prediction_data[['year', 'population', 'bachelor_degree', 'graduate_degree', 'median_income']]
    )

    # Combine predictions into a DataFrame
    future_enrollment_df = prediction_data.copy()
    future_enrollment_df['students'] = future_enrollment.round(0).astype(int)  # Changed key from 'predicted_students' to 'students'

    logger.info("Predicted Enrollment for 2024:\n%s", future_enrollment_df)

    # Add 'type' key to each predicted record
    future_enrollment_records = future_enrollment_df.to_dict(orient='records')
    for record in future_enrollment_records:
        record['type'] = 'predicted'

    return future_enrollment_records
