# COOKED

import json
import numpy as np
import plotly.graph_objs as go
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log that the program has started
logger.info("Starting to load ZIP code similarity data...")

# Load the zip code similarities from the JSON file
with open('zip_code_similarities.json', 'r') as f:
    zip_data = json.load(f)

# Extract ZIP codes and similarity data
zip_codes = []
similarities = []

# Each ZIP code becomes a node
logger.info("Extracting ZIP codes and similarities...")
for entry in zip_data:
    zip_code = entry['zip_code']
    similar_zips = entry['similar_zips']
    
    # For each zip_code, we'll track the similarities and ensure symmetry in the similarity matrix
    for similar_zip in similar_zips:
        zip_codes.append([zip_code, similar_zip['zip_code']])
        similarities.append(similar_zip['similarity'])

# Create a similarity matrix
unique_zips = list(set([z[0] for z in zip_codes] + [z[1] for z in zip_codes]))
zip_index = {zip_code: i for i, zip_code in enumerate(unique_zips)}

n = len(unique_zips)
similarity_matrix = np.ones((n, n))

# Fill the similarity matrix with values (closer to 1 means more similar)
logger.info("Building the similarity matrix...")
for (zip1, zip2), sim in zip(zip_codes, similarities):
    i, j = zip_index[zip1], zip_index[zip2]
    similarity_matrix[i, j] = sim
    similarity_matrix[j, i] = sim  # Symmetry

# Replace NaN or invalid values with 0 or some other fallback
similarity_matrix[np.isnan(similarity_matrix)] = 0
similarity_matrix[np.isinf(similarity_matrix)] = 0

# Perform t-SNE to reduce the similarity matrix to 2D coordinates
logger.info("Starting t-SNE dimensionality reduction to 2D...")
tsne = TSNE(n_components=2, metric='precomputed', random_state=42, perplexity=30, init='random')

# Convert similarity to dissimilarity (1 - similarity)
dissimilarity_matrix = 1 - similarity_matrix
dissimilarity_matrix[dissimilarity_matrix < 0] = 0  # Ensure non-negative values

# Fit t-SNE
coords = tsne.fit_transform(dissimilarity_matrix)

# Log that the plot is being built
logger.info("Building the 2D plot...")

# Plot 2D scatter plot
x, y = coords[:, 0], coords[:, 1]

trace = go.Scatter(
    x=x,
    y=y,
    mode='markers+text',
    marker=dict(
        size=10,
        color=np.arange(len(unique_zips)),
        colorscale='Viridis',
        opacity=0.8
    ),
    text=unique_zips,  # Annotate each point with the zip code
    hoverinfo='text'
)

layout = go.Layout(
    title='2D Similarity of ZIP Codes with t-SNE',
    xaxis=dict(title='X Axis'),
    yaxis=dict(title='Y Axis'),
    margin=dict(l=0, r=0, b=0, t=40),
)

fig = go.Figure(data=[trace], layout=layout)

# Show the 2D plot
logger.info("Displaying the 2D plot...")
fig.show()
