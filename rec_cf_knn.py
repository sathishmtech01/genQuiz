from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from surprise import accuracy

# Sample dataset
data = {
    'client_id': [1, 1, 2, 2, 3, 3, 4, 4, 5],
    'product': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'B', 'C'],
    'rating': [5, 3, 4, 2, 2, 5, 3, 4, 4]
}

df = pd.DataFrame(data)

# Load data into Surprise dataset
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[['client_id', 'product', 'rating']], reader)

# Split the dataset into train and test sets
trainset, testset = train_test_split(data, test_size=0.25)

# Use user-based collaborative filtering
algo = KNNBasic(user_based=True)

# Train the algorithm on the trainset
algo.fit(trainset)

# Test the algorithm on the testset
predictions = algo.test(testset)

# Compute and print Root Mean Squared Error
rmse = accuracy.rmse(predictions)
print(f'RMSE: {rmse}')

# Function to get top-N recommendations for a given client
def get_top_n_recommendations(algo, client_id, n=3):
    # Get a list of all product IDs
    all_products = df['product'].unique()
    
    # Get the products already rated by the client
    rated_products = df[df['client_id'] == client_id]['product'].tolist()
    
    # Get a list of products not rated by the client
    products_to_predict = [product for product in all_products if product not in rated_products]
    
    # Predict ratings for the products not rated by the client
    predictions = [algo.predict(client_id, product) for product in products_to_predict]
    
    # Sort the predictions by estimated rating
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    # Get the top-N highest rated products
    top_n = predictions[:n]
    
    # Return the top-N product recommendations
    return [(pred.iid, pred.est) for pred in top_n]

# Example usage
client_id = 1
top_n_recommendations = get_top_n_recommendations(algo, client_id, n=3)
print(f"Top recommendations for client {client_id}:")
for product, estimated_rating in top_n_recommendations:
    print(f"Product: {product}, Estimated Rating: {estimated_rating}")
