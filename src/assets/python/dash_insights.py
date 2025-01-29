from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load datasets
demographic_data = pd.read_csv('census_zipcode_percentages.csv')
zip_occurrences_data = pd.read_csv('zipcode_occurrences.csv')
enrollment_data = pd.read_csv('enrollment 2019-2023.csv')

# Merge datasets to include occurrences in the demographic data
merged_data = pd.merge(demographic_data, zip_occurrences_data, on="Zip_Code", how="inner")

# Initialize Dash app
app = Dash(__name__)

############################################
############ Ethnicity Pie Chart ###########
############################################

def create_ethnicity_pie_chart(filtered_data):
    ethnicity_columns = ['White_Alone', 'Black_Alone', 'Hispanic_Latino']
    for ethnicity in ethnicity_columns:
        filtered_data[ethnicity] = filtered_data[ethnicity] * filtered_data['Population']
    
    ethnicity_data = filtered_data[[ethnicity for ethnicity in ethnicity_columns]].sum().reset_index()
    ethnicity_data.columns = ['Ethnicity', 'Count']

    pie_chart = px.pie(
        ethnicity_data, 
        names='Ethnicity', 
        values='Count',
        title='Ethnicity Makeup of CBU Freshman ZIP Codes',
        labels={'Count': 'Total Population'}
    )
    return pie_chart


@app.callback(
    Output('ethnicity-pie-chart', 'figure'),
    Output('slider-output-container', 'children'),
    Input('top-zip-slider', 'value')
)
def update_pie_chart(top_percentage):
    num_zipcodes = int(len(merged_data) * (top_percentage / 100))
    filtered_top_zipcodes = merged_data.sort_values(by='Population', ascending=False).head(num_zipcodes)

    pie_chart = create_ethnicity_pie_chart(filtered_top_zipcodes)
    slider_output = f"Top {top_percentage}% of ZIP codes"

    return pie_chart, slider_output

############################################
######## Enrollment Trends Chart ###########
############################################

enrollment_data = enrollment_data[enrollment_data['Start Term and Year'].str.contains('Fall')]
enrollment_data['Term_Year'] = enrollment_data['Start Term and Year']

zip_trends = enrollment_data.groupby(['Mailing Zip/Postal Code', 'Term_Year']).size().reset_index(name='Count')

@app.callback(
    Output('zip-trend-line-chart', 'figure'),
    Input('trend-filter', 'value')
)
def update_zip_trend_chart(trend_type):
    if trend_type == 'top':
        top_zip_codes = zip_trends.groupby('Mailing Zip/Postal Code')['Count'].sum().nlargest(10).index
        data = zip_trends[zip_trends['Mailing Zip/Postal Code'].isin(top_zip_codes)]
    elif trend_type == 'increasing':
        zip_trend_changes = zip_trends.pivot(index='Term_Year', columns='Mailing Zip/Postal Code', values='Count').fillna(0).diff().sum()
        increasing_zip_codes = zip_trend_changes[zip_trend_changes > 0].nlargest(10).index
        data = zip_trends[zip_trends['Mailing Zip/Postal Code'].isin(increasing_zip_codes)]
    else:
        zip_trend_changes = zip_trends.pivot(index='Term_Year', columns='Mailing Zip/Postal Code', values='Count').fillna(0).diff().sum()
        decreasing_zip_codes = zip_trend_changes[zip_trend_changes < 0].nsmallest(10).index
        data = zip_trends[zip_trends['Mailing Zip/Postal Code'].isin(decreasing_zip_codes)]

    figure = px.line(
        data,
        x='Term_Year',
        y='Count',
        color='Mailing Zip/Postal Code',
        title='Enrollment Trends by ZIP Codes',
        labels={'Term_Year': 'Year', 'Count': 'Student Count'}
    )
    return figure

############################################
########### Dynamic Chord Diagram ##########
############################################
############################################

@app.callback(
    Output('chord-diagram', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_chord_diagram(selected_year, selected_state):
    filtered_data = enrollment_data.copy()
    if selected_year:
        filtered_data = filtered_data[filtered_data['Start Term and Year'] == selected_year]
    if selected_state:
        filtered_data = filtered_data[filtered_data['Mailing State/Province'] == selected_state]

    # count students by city
    student_counts = filtered_data.groupby('Mailing City')['Start Term and Year'].count().reset_index()
    student_counts.columns = ['Mailing City', 'Count']
    target_region = 'CBU'

    # source and target nodes
    all_nodes = list(student_counts['Mailing City']) + [target_region]
    source_indices = [all_nodes.index(city) for city in student_counts['Mailing City']]
    target_indices = [all_nodes.index(target_region)] * len(source_indices)

    figure = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="blue"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=student_counts['Count']
        )
    )])

    figure.update_layout(title_text="Enrollment Origins by Region (Chord Diagram)", font_size=10)
    return figure

############################################
###### Ethnicity and Income Correlation ####
############################################

@app.callback(
    Output('income-distribution-histogram', 'figure'),
    Input('state-dropdown', 'value')
)
def update_income_distribution(selected_state):
    filtered_data = merged_data.copy()

    # Filter by state
    if selected_state:
        filtered_data = filtered_data[filtered_data['Mailing State/Province'] == selected_state]

    figure = px.histogram(
        filtered_data,
        x='Median_Income',
        nbins=20,  
        title='Income Distribution Across ZIP Codes',
        labels={'Median_Income': 'Median Income'},
        template='plotly_white'
    )

    # layout
    figure.update_layout(
        xaxis_title='Median Income ($)',
        yaxis_title='Number of ZIP Codes',
        bargap=0.2
    )

    return figure





############################################
################ App Layout ################
############################################

app.layout = html.Div([
    # First row of quadrants
    html.Div([
        # Ethnicity Pie Chart
        html.Div([
            dcc.Graph(id='ethnicity-pie-chart'),
            html.Div([
                dcc.Slider(
                    id='top-zip-slider',
                    min=1,
                    max=100,
                    step=1,
                    value=100,
                    marks={i: f"{i}%" for i in range(10, 101, 10)},
                    tooltip={"placement": "right", "always_visible": True},
                    vertical=True
                ),
            ], style={'position': 'absolute', 'top': '7.5%', 'left': '5%', 'height': '20%'}),
            html.Div(id="slider-output-container", style={'textAlign': 'center', 'marginTop': 0}),
        ], style={'position': 'relative', 'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='zip-trend-line-chart'),
            html.Div([
                dcc.Dropdown(
                    id='trend-filter',
                    options=[
                        {'label': 'Top ZIP Codes', 'value': 'top'},
                        {'label': 'Increasing Trends', 'value': 'increasing'},
                        {'label': 'Decreasing Trends', 'value': 'decreasing'}
                    ],
                    value='top',
                    clearable=False
                )
            ], style={
                'position': 'absolute',
                'top': '12.5%',
                'left': '8%',
                'width': '30%'
            })
        ], style={'position': 'relative', 'width': '48%', 'display': 'inline-block'})
    ]),

        # Dropdown filters
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in enrollment_data['Start Term and Year'].unique()],
                placeholder='Select Year',
                style={'width': '30%', 'margin': '10px auto'}
            ),

            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in enrollment_data['Mailing State/Province'].unique()],
                placeholder='Select State',
                style={'width': '30%', 'margin': '10px auto'}
            ),
        ]),
        
    
        html.Div([
            # Dynamic Chord Diagram (Left Bottom)
            html.Div([
                dcc.Graph(id='chord-diagram'),
            ], style={'width': '48%', 'display': 'inline-block'}),

            # Income Distribution Histogram (Right Bottom)
            html.Div([
                dcc.Graph(id='income-distribution-histogram'),
            ], style={'width': '48%', 'display': 'inline-block', 'position': 'relative'}),
        ], style={'display': 'flex', 'justify-content': 'space-around'})

])

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
