#!/usr/bin/env python3
"""
Test script for Music Explorer application
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def test_data_loading():
    """Test data loading functionality."""
    print("Testing data loading...")
    try:
        df = pd.read_csv('data/spotify_tracks_enhanced.csv')
        print(f"✅ Enhanced dataset loaded: {len(df)} tracks")
        print(f"   Genres: {sorted(df['genre'].unique())}")
        print(f"   Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print("❌ Enhanced dataset not found")
        return None

def test_knn_model(df):
    """Test KNN model creation."""
    print("\nTesting KNN model...")
    try:
        feature_cols = ['x', 'y', 'energy', 'danceability', 'valence', 'acousticness', 'instrumentalness']
        features = df[feature_cols].values
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
        knn.fit(features_scaled)
        
        print("✅ KNN model created successfully")
        return knn, scaler, feature_cols
    except Exception as e:
        print(f"❌ KNN model creation failed: {e}")
        return None, None, None

def test_clustering(df):
    """Test clustering functionality."""
    print("\nTesting clustering...")
    try:
        feature_cols = ['x', 'y']
        features = df[feature_cols].values
        
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(features)
        
        print(f"✅ Clustering successful: {len(np.unique(clusters))} clusters")
        return clusters, kmeans
    except Exception as e:
        print(f"❌ Clustering failed: {e}")
        return None, None

def test_recommendations(df, knn_model, scaler, feature_cols):
    """Test recommendation system."""
    print("\nTesting recommendations...")
    try:
        # Test with first track
        test_track = df.iloc[0]
        track_features = test_track[feature_cols].values.reshape(1, -1)
        track_features_scaled = scaler.transform(track_features)
        
        distances, indices = knn_model.kneighbors(track_features_scaled)
        recommendations = df.iloc[indices[0][1:6]]  # Get 5 recommendations
        
        print(f"✅ Recommendations generated for '{test_track['track_name']}'")
        print("   Similar tracks:")
        for _, track in recommendations.iterrows():
            print(f"   - {track['track_name']} by {track['artist_name']}")
        
        return True
    except Exception as e:
        print(f"❌ Recommendations failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎵 Music Explorer - Application Test Suite")
    print("=" * 50)
    
    # Test data loading
    df = test_data_loading()
    if df is None:
        print("\n❌ Cannot proceed without data")
        return
    
    # Test KNN model
    knn_model, scaler, feature_cols = test_knn_model(df)
    if knn_model is None:
        print("\n❌ Cannot proceed without KNN model")
        return
    
    # Test clustering
    clusters, kmeans_model = test_clustering(df)
    if clusters is None:
        print("\n❌ Cannot proceed without clustering")
        return
    
    # Test recommendations
    recommendations_ok = test_recommendations(df, knn_model, scaler, feature_cols)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Data loading: ✅")
    print(f"   KNN model: ✅")
    print(f"   Clustering: ✅")
    print(f"   Recommendations: {'✅' if recommendations_ok else '❌'}")
    
    if all([df is not None, knn_model is not None, clusters is not None, recommendations_ok]):
        print("\n🎉 All tests passed! The application should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()