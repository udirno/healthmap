import pandas as pd

from utils import compute_distance_series


def test_recommendations_distance_sorting():
    df = pd.DataFrame({
        'track_id': ['a','b','c'],
        'track_name': ['A','B','C'],
        'artist_name': ['X','Y','Z'],
        'genre': ['rock','rock','rock'],
        'x': [0.0, 1.0, 2.0],
        'y': [0.0, 0.0, 0.0],
        'danceability':[0.5,0.5,0.5],
        'energy':[0.5,0.5,0.5],
        'valence':[0.5,0.5,0.5],
        'acousticness':[0.1,0.1,0.1],
        'instrumentalness':[0.0,0.0,0.0],
        'liveness':[0.1,0.1,0.1],
        'speechiness':[0.1,0.1,0.1],
        'tempo':[120,120,120],
        'loudness':[-6,-6,-6],
    })
    row = df.iloc[0]
    d = compute_distance_series(df, row)
    # closest should be index 1 (distance 1), then 2 (distance 2)
    top2 = d.nsmallest(2).index.tolist()
    assert top2 == [1, 2]

