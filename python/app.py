# enrollment_predictor.py

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import logging
import re

app = Flask(__name__)

# Enable CORS for the entire Flask app
CORS(app)

# Configure logging
logging.basicConfig(
    filename='enrollment_predictor.log',
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s:%(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Function to clean and extract start year from "Start Term and Year"
def extract_start_year(term_year):
    try:
        # Use regex to find a four-digit year
        match = re.search(r'(\d{4})', str(term_year))
        if match:
            year = int(match.group(1))
            return year
        else:
            raise ValueError(f"No year found in '{term_year}'")
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to extract year from '{term_year}': {e}")
        return np.nan

def get_enrollment_data():
    try:
        # Step 1: Read CSV Files (Ensure these paths are correct)
        enrollment_df = pd.read_csv('../csvdata/enrollment 2019-2023.csv')
        census_zip_df = pd.read_csv('../csvdata/census_zipcode_demographics_2022.csv')
        census_city_df = pd.read_csv('../csvdata/census_city_demographics_2022.csv')

        logger.debug(f"Enrollment DataFrame Shape: {enrollment_df.shape}")
        logger.debug(f"Census Zip DataFrame Shape: {census_zip_df.shape}")
        logger.debug(f"Census City DataFrame Shape: {census_city_df.shape}")

        logger.debug(f"Enrollment DataFrame Columns: {enrollment_df.columns.tolist()}")
        logger.debug(f"Census Zip DataFrame Columns: {census_zip_df.columns.tolist()}")
        logger.debug(f"Census City DataFrame Columns: {census_city_df.columns.tolist()}")

        # Step 2: Clean and Standardize Data
        enrollment_df.columns = enrollment_df.columns.str.strip()
        census_zip_df.columns = census_zip_df.columns.str.strip()
        census_city_df.columns = census_city_df.columns.str.strip()

        # Step 3: Extract Start Year and Clean Data
        enrollment_df['Start Year'] = enrollment_df['Start Term and Year'].apply(extract_start_year)
        logger.debug("After extracting Start Year:")
        logger.debug(enrollment_df[['Start Term and Year', 'Start Year']].head())

        # Drop rows with invalid Start Year
        initial_count = enrollment_df.shape[0]
        enrollment_df = enrollment_df.dropna(subset=['Start Year'])
        final_count = enrollment_df.shape[0]
        dropped_rows = initial_count - final_count
        if dropped_rows > 0:
            logger.debug(f"Dropped {dropped_rows} rows due to invalid Start Year.")

        logger.debug(f"Enrollment DataFrame Shape after dropping invalid Start Year: {enrollment_df.shape}")

        # Step 4: Aggregate Enrollment Data to Count Students per ZIP Code and Year
        # Assuming each row represents one student enrollment
        aggregated_enrollment = enrollment_df.groupby(['Start Year', 'Mailing Zip/Postal Code']).size().reset_index(name='students')
        logger.debug(f"Aggregated Enrollment Data Shape: {aggregated_enrollment.shape}")
        logger.debug("Aggregated Enrollment Data Sample:")
        logger.debug(aggregated_enrollment.head())

        # **New Step: Adjust 'students' counts per year to match specified totals**

        # Your specified totals per year
        specified_totals = {
            2019: 11045,
            2020: 11317,
            2021: 11491,
            2022: 11384,
            2023: 11407,
        }

        # Calculate actual totals per year from aggregated data
        actual_totals = aggregated_enrollment.groupby('Start Year')['students'].sum().to_dict()

        # Adjust the 'students' counts per year
        def adjust_students_counts(df, specified_totals, actual_totals):
            df = df.copy()
            df['adjusted_students'] = df['students']
            for year in specified_totals.keys():
                if actual_totals.get(year, 0) > 0:
                    scaling_factor = specified_totals[year] / actual_totals[year]
                    df.loc[df['Start Year'] == year, 'adjusted_students'] = df.loc[df['Start Year'] == year, 'students'] * scaling_factor
                else:
                    # Handle years with zero actual total to avoid division by zero
                    logger.warning(f"Actual total students for year {year} is zero. Cannot scale counts.")
            return df

        adjusted_aggregated_enrollment = adjust_students_counts(aggregated_enrollment, specified_totals, actual_totals)

        # Replace 'students' column with 'adjusted_students'
        aggregated_enrollment['students'] = adjusted_aggregated_enrollment['adjusted_students']

        # Ensure 'students' counts are integers
        aggregated_enrollment['students'] = aggregated_enrollment['students'].round().astype(int)

        # Step 5: Clean ZIP Codes
        aggregated_enrollment['Mailing Zip/Postal Code'] = aggregated_enrollment['Mailing Zip/Postal Code'].astype(str).str.zfill(5)
        census_zip_df['Zip_Code'] = census_zip_df['Zip_Code'].astype(str).str.zfill(5)

        logger.debug("After cleaning ZIP Codes:")
        logger.debug(aggregated_enrollment[['Start Year', 'Mailing Zip/Postal Code', 'students']].head())
        logger.debug(census_zip_df[['Zip_Code']].head())

        # Step 6: Merge Aggregated Enrollment Data with Census Zip Code Data on ZIP codes
        merged_zip_df = pd.merge(
            aggregated_enrollment,
            census_zip_df,
            how='left',
            left_on='Mailing Zip/Postal Code',
            right_on='Zip_Code',
            suffixes=('_enroll', '_census_zip')
        )
        logger.debug(f"Merged ZIP DataFrame Shape: {merged_zip_df.shape}")
        logger.debug("Merged ZIP DataFrame Sample:")
        logger.debug(merged_zip_df.head())

        # Step 7: Check for Missing Demographic Data Post-Merge
        missing_demographics_zip = merged_zip_df[merged_zip_df['Population'].isna()]
        if not missing_demographics_zip.empty:
            logger.warning(f"There are {missing_demographics_zip.shape[0]} unmatched ZIP codes after merge.")
            logger.warning("Sample unmatched ZIP entries:")
            logger.warning(missing_demographics_zip.head())
            # Decide on handling strategy: drop unmatched entries
            merged_zip_df = merged_zip_df.dropna(subset=['Population'])
            logger.debug(f"Merged ZIP DataFrame Shape after dropping unmatched ZIP codes: {merged_zip_df.shape}")
        else:
            logger.debug("All ZIP codes matched successfully.")

        # Step 8: Prepare Census City Data
        # Clean and standardize city names and state codes
        census_city_df['City'] = census_city_df['City'].str.upper().str.strip()
        census_city_df['State_Code'] = census_city_df['State_Code'].astype(str).str.upper().str.strip()

        # Aggregate city demographics by City and State to ensure uniqueness
        census_city_df = census_city_df.groupby(['City', 'State_Code']).mean().reset_index()
        logger.debug(f"Aggregated Census City Data Shape: {census_city_df.shape}")
        logger.debug("Aggregated Census City Data Sample:")
        logger.debug(census_city_df.head())

        # Step 9: Merge with Census City Data
        # To merge city-level data, we need to map ZIP codes to cities and states
        # Check if 'census_zipcode_demographics_2022.csv' includes 'City' and 'State_Code'
        # If not, this step will be skipped

        if 'City' in census_zip_df.columns and 'State_Code' in census_zip_df.columns:
            logger.debug("Merging with Census City Data based on 'City' and 'State_Code'.")
            merged_full_df = pd.merge(
                merged_zip_df,
                census_city_df,
                how='left',
                left_on=['City', 'State_Code'],  # Replace with actual column names if different
                right_on=['City', 'State_Code'],
                suffixes=('', '_census_city')
            )
            logger.debug(f"Merged Full DataFrame Shape: {merged_full_df.shape}")
            logger.debug("Merged Full DataFrame Sample:")
            logger.debug(merged_full_df.head())
        else:
            logger.warning("City and State_Code not available in Census Zip Data; skipping city-level merge.")
            merged_full_df = merged_zip_df.copy()

        # Step 10: Select Relevant Features for Modeling
        # Choose demographic features that are likely to influence enrollment
        required_columns = [
            'Start Year', 'students', 'Population', 
            'Median_Income', 'Median_Age', 'Bachelor_Degree', 
            'Total_Education_Population', 'Graduate_Professional_Degree',
            'White_Alone', 'Black_Alone', 'Hispanic_Latino', 'Employment_Status',
            'Unemployment', 'Total_Health_Insurance_Coverage', 'Without_Health_Insurance',
            'Total_Pop_Poverty_Status', 'Below_Poverty_Level', 'Median_Home_Value',
            'Median_Gross_Rent', 'Owner_Occupied_Units', 'Renter_Occupied_Units',
            'Means_of_Transportation_to_Work', 'Total_Pop_Marital_Status',
            'Married_Population', 'ZCTA'
        ]

        # Check for missing required columns
        missing_cols = [col for col in required_columns if col not in merged_full_df.columns]
        if missing_cols:
            logger.error(f"Missing required columns in merged DataFrame: {missing_cols}")
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Select and rename columns for consistency
        selected_df = merged_full_df[required_columns].copy()
        selected_df = selected_df.rename(columns={
            'Start Year': 'year',
            'Population': 'population',
            'Median_Income': 'median_income',
            'Median_Age': 'median_age',
            'Bachelor_Degree': 'bachelor_degree',
            'Total_Education_Population': 'total_education_population',
            'Graduate_Professional_Degree': 'graduate_professional_degree',
            'White_Alone': 'white_alone',
            'Black_Alone': 'black_alone',
            'Hispanic_Latino': 'hispanic_latino',
            'Employment_Status': 'employment_status',
            'Unemployment': 'unemployment',
            'Total_Health_Insurance_Coverage': 'total_health_insurance_coverage',
            'Without_Health_Insurance': 'without_health_insurance',
            'Total_Pop_Poverty_Status': 'total_pop_poverty_status',
            'Below_Poverty_Level': 'below_poverty_level',
            'Median_Home_Value': 'median_home_value',
            'Median_Gross_Rent': 'median_gross_rent',
            'Owner_Occupied_Units': 'owner_occupied_units',
            'Renter_Occupied_Units': 'renter_occupied_units',
            'Means_of_Transportation_to_Work': 'means_of_transportation_to_work',
            'Total_Pop_Marital_Status': 'total_pop_marital_status',
            'Married_Population': 'married_population',
            'ZCTA': 'zcta'
        })

        logger.debug(f"Selected and Renamed DataFrame Shape: {selected_df.shape}")
        logger.debug("Selected and Renamed DataFrame Sample:")
        logger.debug(selected_df.head())

        # Step 11: Handle Missing Values in Demographic Features
        # For simplicity, drop rows with any missing values
        initial_count = selected_df.shape[0]
        selected_df = selected_df.dropna()
        final_count = selected_df.shape[0]
        dropped_rows = initial_count - final_count
        if dropped_rows > 0:
            logger.debug(f"Dropped {dropped_rows} rows due to missing demographic data.")

        logger.debug(f"DataFrame Shape after dropping missing values: {selected_df.shape}")

        # Step 12: Encode Categorical Variables
        # Identify categorical columns that need encoding
        categorical_cols = ['employment_status', 'means_of_transportation_to_work']
        for col in categorical_cols:
            if col in selected_df.columns:
                selected_df = pd.get_dummies(selected_df, columns=[col], drop_first=True)
                logger.debug(f"Encoded categorical column: {col}")

        logger.debug(f"DataFrame Shape after encoding categorical variables: {selected_df.shape}")
        logger.debug(f"DataFrame Columns after encoding: {selected_df.columns.tolist()}")

        # Step 13: Prepare Data for Modeling
        # Define feature columns and target variable
        target = 'students'
        features = selected_df.columns.tolist()
        features.remove(target)

        X = selected_df[features]
        y = selected_df[target]

        logger.debug(f"Features selected for modeling: {features}")
        logger.debug(f"Feature DataFrame Shape: {X.shape}")
        logger.debug(f"Target Series Shape: {y.shape}")

        # Check if X is empty
        if X.empty:
            logger.error("Feature set X is empty after processing.")
            raise ValueError("Feature set X is empty. Check data processing steps.")

        # Step 14: Fit the Multivariate Linear Regression Model
        model = LinearRegression()
        model.fit(X, y)
        logger.debug("Fitted Linear Regression Model.")

        # Step 15: Predict Future Enrollment
        # For prediction, we'll use the latest available demographic data
        latest_year = selected_df['year'].max()
        latest_data = selected_df[selected_df['year'] == latest_year]

        logger.debug(f"Latest Year in Data: {latest_year}")
        logger.debug(f"Latest Year Data Shape: {latest_data.shape}")

        if latest_data.empty:
            logger.error(f"No data available for the latest year ({latest_year}) to make predictions.")
            raise ValueError("Insufficient data for making predictions.")

        # Prepare future features per 'zcta'
        future_features = latest_data.copy()
        future_features['year'] = future_features['year'] + 1  # Next year

        # Ensure that all feature columns are present in future_features
        missing_features = set(features) - set(future_features.columns)
        for feature in missing_features:
            future_features[feature] = 0  # Assign default value or estimate appropriately

        # Reorder columns to match training features
        future_features = future_features[features]

        # Predict enrollment per 'zcta' for next year
        predicted_students = model.predict(future_features)

        # Add 'zcta' and 'predicted_students' to dataframe
        future_features['predicted_students'] = predicted_students

        # Sum predicted students over 'zcta' to get total predicted students
        total_predicted_students = future_features['predicted_students'].sum()
        total_predicted_students = max(int(round(total_predicted_students)), 0)  # Ensure non-negative

        logger.debug(f"Predicted total enrollment for year {future_features['year'].iloc[0]}: {total_predicted_students}")

        future_predictions = [{'year': int(future_features['year'].iloc[0]), 'students': total_predicted_students}]

        # Step 16: Prepare the Combined Response Data
        # Historical data: sum of students per year
        historical_data = selected_df.groupby('year')['students'].sum().reset_index()
        historical_response = historical_data.to_dict(orient='records')

        # Combine historical and future predictions
        combined_response = historical_response + future_predictions

        logger.debug("Prepared combined historical and predicted enrollment data.")
        logger.debug("Combined Response Sample:")
        logger.debug(combined_response[:5])  # Log first 5 entries

        return combined_response
    
    except Exception as e: 
        print(f"Error in get_enrollment_data: {e}") 
        raise e  # Re-raise exception to be handled in the route

    # Define the enrollment data route outside the data processing function
@app.route('/enrollment-data', methods=['GET'])
def enrollment_data():
    try:
        data = get_enrollment_data()
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error in /enrollment-data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
        app.run(debug=True, port=5000)