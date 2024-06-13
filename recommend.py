import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Sample data
data = {
    'id': [1, 1, 1, 2, 2, 2],
    'product_id': [101, 102, 103, 201, 202, 203],
    'income': [30000, 45000, 60000, 75000, 90000, 105000],
    'capital': [5000, 15000, 25000, 35000, 45000, 55000]
}

# Create DataFrame
df = pd.DataFrame(data)

# Define a function to normalize data within each id group
def normalize_group(group):
    scaler = MinMaxScaler()
    group[['income_normalized', 'capital_normalized']] = scaler.fit_transform(group[['income', 'capital']])
    return group

# Apply normalization function to each group by 'id'
df = df.groupby('id').apply(normalize_group)

# Compute the combined score (simple average)
df['combined_score'] = df[['income_normalized', 'capital_normalized']].mean(axis=1)

# Define thresholds for ratings (example using quantiles of the combined score)
thresholds = df['combined_score'].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).tolist()

# Define a function to convert combined score to rating
def convert_to_rating(value, thresholds):
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return i + 1
    return len(thresholds)

# Apply the function to the combined score
df['rating'] = df['combined_score'].apply(lambda x: convert_to_rating(x, thresholds))

# Display the resulting DataFrame
print(df[['id', 'product_id', 'income', 'capital', 'combined_score', 'rating']])
