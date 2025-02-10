import pandas as pd

# Load the original CSV file
csv_file_path = 'census_zipcode_demographics_2022.csv'
data = pd.read_csv(csv_file_path)

# Overwrite educational attainment fields with percentage values, rounded to 4 decimal places
data['Bachelor_Degree'] = (data['Bachelor_Degree'] / data['Total_Education_Population']).round(4)
data['Graduate_Professional_Degree'] = (data['Graduate_Professional_Degree'] / data['Total_Education_Population']).round(4)

# Overwrite racial demographics fields with percentage values based on Population, rounded to 4 decimal places
data['White_Alone'] = (data['White_Alone'] / data['Population']).round(4)
data['Black_Alone'] = (data['Black_Alone'] / data['Population']).round(4)
data['Hispanic_Latino'] = (data['Hispanic_Latino'] / data['Population']).round(4)

# Overwrite Unemployment field with percentage based on Employment_Status, rounded to 4 decimal places
data['Unemployment'] = (data['Unemployment'] / data['Employment_Status']).round(4)

# Overwrite Without_Health_Insurance with percentage based on Total_Health_Insurance_Coverage, rounded to 4 decimal places
data['Without_Health_Insurance'] = (data['Without_Health_Insurance'] / data['Total_Health_Insurance_Coverage']).round(4)

# Overwrite Below_Poverty_Level with percentage based on Total_Pop_Poverty_Status, rounded to 4 decimal places
data['Below_Poverty_Level'] = (data['Below_Poverty_Level'] / data['Total_Pop_Poverty_Status']).round(4)

# Overwrite Married_Population with percentage based on Total_Pop_Marital_Status, rounded to 4 decimal places
data['Married_Population'] = (data['Married_Population'] / data['Total_Pop_Marital_Status']).round(4)

# Save the updated CSV, replacing fields with their percentage values
updated_csv_path = 'census_zipcode_percentages.csv'
data.to_csv(updated_csv_path, index=False)

print(f"Updated CSV saved as {updated_csv_path}")
