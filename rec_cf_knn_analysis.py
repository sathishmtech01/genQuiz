import pandas as pd
from surprise import Dataset, Reader, KNNBasic, accuracy
from sklearn.model_selection import train_test_split
from collections import defaultdict

# Sample dataset
data = {
    'client_id': [1, 1, 2, 2, 3, 3, 4, 4, 5],
    'product': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'B', 'C'],
    'rating': [5, 3, 4, 2, 2, 5, 3, 4, 4]
}

df = pd.DataFrame(data)

# Define a reader to specify the rating scale
reader = Reader(rating_scale=(1, 5))

# Split the dataset based on client_id
client_ids = df['client_id'].unique()
train_ids, test_ids = train_test_split(client_ids, test_size=0.25, random_state=42)

train_df = df[df['client_id'].isin(train_ids)]
test_df = df[df['client_id'].isin(test_ids)]

# Save the trainset and testset DataFrames to CSV files
train_df.to_csv('trainset.csv', index=False)
test_df.to_csv('testset.csv', index=False)
# Load training data from CSV into a pandas DataFrame
train_df = pd.read_csv('trainset.csv')

# Load test data from CSV into a pandas DataFrame
test_df = pd.read_csv('testset.csv')

# Load training data into Surprise dataset
train_data = Dataset.load_from_df(train_df[['client_id', 'product', 'rating']], reader)
trainset = train_data.build_full_trainset()

# Load test data into a list of (user, item, rating) tuples
testset = list(test_df.itertuples(index=False, name=None))
# Use user-based collaborative filtering
algo = KNNBasic(user_based=True)

# Train the algorithm on the trainset
algo.fit(trainset)

# Test the algorithm on the testset
predictions = algo.test(testset)

# Compute and print Root Mean Squared Error
rmse = accuracy.rmse(predictions)
print(f'RMSE: {rmse}')
def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.'''
    
    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))
    
    # Then sort the predictions for each user and retrieve the top-N items.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    
    return top_n

def precision_recall_at_k(predictions, k=10, threshold=3.5):
    '''Return precision and recall at k metrics for each user.'''
    
    # First map the predictions to each user.
    user_est_true = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))
    
    precisions = dict()
    recalls = dict()
    
    # Then compute precision and recall for each user
    for uid, user_ratings in user_est_true.items():
        
        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        
        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        
        # Number of recommended items in top k
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])
        
        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])
        
        # Precision@K: Proportion of recommended items that are relevant
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 1
        
        # Recall@K: Proportion of relevant items that are recommended
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 1
    
    # Compute average precision and recall
    precision = sum(prec for prec in precisions.values()) / len(precisions)
    recall = sum(rec for rec in recalls.values()) / len(recalls)
    
    return precision, recall

# Compute precision and recall at k
precision, recall = precision_recall_at_k(predictions, k=5, threshold=3.5)

print(f'Precision: {precision}')
print(f'Recall: {recall}')
