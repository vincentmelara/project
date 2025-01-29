from dash import Dash, dcc, html, Input, Output
import pandas as pd

# Load datasets
demographic_data = pd.read_csv('census_zipcode_percentages.csv')
enrollment_data = pd.read_csv('enrollment 2019-2023.csv')
city_images_data = pd.read_csv('city_images.csv')  # Load city images CSV

# Clean and prepare data
enrollment_data['Mailing Zip/Postal Code'] = enrollment_data['Mailing Zip/Postal Code'].astype(str)
demographic_data['Zip_Code'] = demographic_data['Zip_Code'].astype(str)

# Merge datasets to include states and cities
merged_data = pd.merge(
    demographic_data,
    enrollment_data[['Mailing Zip/Postal Code', 'Mailing City', 'Mailing State/Province']],
    left_on='Zip_Code',
    right_on='Mailing Zip/Postal Code',
    how='left'
).drop_duplicates(subset=['Zip_Code'])

# Filter for California ZIP codes only
california_data = merged_data[merged_data['Mailing State/Province'] == "CA"]

# Merge city images into California data
california_data = pd.merge(
    california_data,
    city_images_data,
    left_on='Mailing City',
    right_on='City',
    how='left'
)

# Prepare ZIP code options for the dropdown
zip_options = [{'label': zip_code, 'value': zip_code} for zip_code in california_data['Zip_Code'].unique()]

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    # Filters
    html.Div([
        dcc.Dropdown(
            id='zip-code-dropdown',
            options=zip_options,
            placeholder='Select a ZIP Code',
            style={'width': '30%', 'fontSize': '16px', 'padding': '0px'}
        )

    ], style={'margin': '20px'}),

    # Display selected profile
    html.Div(id='zip-code-profile', style={'margin': '20px'})
])

# Callback to filter and display ZIP code profile
@app.callback(
    Output('zip-code-profile', 'children'),
    Input('zip-code-dropdown', 'value')
)
def update_zip_code_profile(selected_zip):
    # Debugging: Check if a ZIP code is selected
    print(f"Selected ZIP Code: {selected_zip}")
    
    # Filter data for the selected ZIP code
    if not selected_zip:
        return html.Div("None Selected", style={'color': 'red'})
    
    filtered_data = california_data[california_data['Zip_Code'] == selected_zip]

    # Debugging: Print filtered data
    print("Filtered Data:")
    print(filtered_data)

    # If filtered data is empty
    if filtered_data.empty:
        return html.Div("No data available for the selected ZIP code.", style={'color': 'red'})

    # Calculate city population
    city_name = filtered_data.iloc[0]['Mailing City']
    city_population = california_data[california_data['Mailing City'] == city_name]['Population'].sum()
    city_image_url = filtered_data.iloc[0]['Image_URL']  # Get city image URL

    # Create profile display for selected ZIP code
    zip_profile = filtered_data.iloc[0]
    children = []

    # Add city image if available
    if pd.notna(city_image_url):
        children.append(html.Div([
            html.Img(src=city_image_url, style={'maxWidth': '300px', 'maxHeight': '300px', 'marginBottom': '20px'}),
        ]))
    
    children.extend([
        html.H3(f"Profile for ZIP Code: {zip_profile['Zip_Code']}"),
        html.P(f"City: {city_name}"),
        html.P(f"State: California (CA)"),
        html.P(f"City Population: {city_population:,}"),
        html.P(f"ZIP Code Population: {zip_profile['Population']:,}"),
        html.P(f"Median Income: ${zip_profile['Median_Income']:,}"),
        html.P(f"Median Age: {zip_profile['Median_Age']} years"),
        html.P(f"Educational Attainment:"),
        html.Ul([
            html.Li(f"Bachelor's Degree: {zip_profile['Bachelor_Degree']*100:.1f}%"),
            html.Li(f"Graduate/Professional Degree: {zip_profile['Graduate_Professional_Degree']*100:.1f}%"),
        ]),
        html.P(f"Ethnic Composition:"),
        html.Ul([
            html.Li(f"White Alone: {zip_profile['White_Alone']*100:.1f}%"),
            html.Li(f"Black Alone: {zip_profile['Black_Alone']*100:.1f}%"),
            html.Li(f"Hispanic or Latino: {zip_profile['Hispanic_Latino']*100:.1f}%"),
        ]),
        html.P(f"Median Home Value: ${zip_profile['Median_Home_Value']:,}"),
        html.P(f"Median Gross Rent: ${zip_profile['Median_Gross_Rent']:,}")
    ])
    
    return html.Div(children)


if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
