import pandas as pd

# Load your dataset
file_path = 'census_zipcode_percentages.csv'
df = pd.read_csv(file_path)

# Ensure ZIP codes are padded to 5 digits
df['Zip_Code'] = df['Zip_Code'].astype(str).str.zfill(5)

# Save the modified dataset
output_path = 'census_zipcodes_11_10.csv'
df.to_csv(output_path, index=False)

print(f"Updated dataset saved to {output_path}")
