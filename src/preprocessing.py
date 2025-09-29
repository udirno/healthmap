import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import umap

class AudioFeatureProcessor:
    def __init__(self):
        self.feature_columns = [
            'danceability', 'energy', 'speechiness', 'acousticness',
            'instrumentalness', 'liveness', 'valence', 'tempo', 'loudness'
        ]
        self.scaler = StandardScaler()
        self.reducer = None
        
    def preprocess_features(self, df):
        """Apply standardization to audio feature matrix."""
        features = df[self.feature_columns].values
        features_scaled = self.scaler.fit_transform(features)
        return features_scaled
    
    def apply_umap(self, features, **kwargs):
        """Generate 2D embedding using UMAP algorithm."""
        default_params = {
            'n_neighbors': 15,
            'min_dist': 0.1,
            'metric': 'euclidean',
            'random_state': 42,
            'n_components': 2
        }
        default_params.update(kwargs)
        
        self.reducer = umap.UMAP(**default_params)
        embedding = self.reducer.fit_transform(features)
        return embedding
    
    def embedding_quality_metrics(self, original_features, embedding):
        """Assess dimensionality reduction preservation quality."""
        from scipy.spatial.distance import pdist
        from scipy.stats import pearsonr
        
        # Distance preservation correlation
        orig_distances = pdist(original_features[:100])  # Sample for efficiency
        embed_distances = pdist(embedding[:100])
        correlation, p_value = pearsonr(orig_distances, embed_distances)
        
        return {
            'distance_correlation': correlation,
            'p_value': p_value,
            'embedding_variance': np.var(embedding, axis=0)
        }
