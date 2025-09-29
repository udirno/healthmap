import pandas as pd
import numpy as np

from utils import get_color_map, validate_schema, compute_distance_series


def test_get_color_map_stable_assignment():
    genres = ['rock', 'pop', 'jazz']
    m1 = get_color_map(genres)
    m2 = get_color_map(genres)
    assert m1 == m2
    assert set(m1.keys()) == set(genres)


def test_validate_schema_pass_and_ranges():
    df = pd.DataFrame({
        'track_id': ['a','b'],
        'track_name': ['t1','t2'],
        'artist_name': ['ar1','ar2'],
        'genre': ['rock','pop'],
        'danceability': [0.5, 0.9],
        'energy': [0.2, 0.8],
        'valence': [0.1, 0.7],
        'acousticness': [0.2, 0.3],
        'instrumentalness': [0.0, 0.1],
        'liveness': [0.1, 0.2],
        'speechiness': [0.1, 0.1],
        'tempo': [120.0, 100.0],
        'loudness': [-6.0, -9.0],
        'x': [1.0, -1.0],
        'y': [0.5, -0.5],
    })
    report = validate_schema(df.copy())
    assert report['ok'] is True

    df_bad = df.copy()
    df_bad.loc[0, 'energy'] = 1.5
    report2 = validate_schema(df_bad.copy())
    assert report2['ok'] is False
    assert 'energy' in report2['bad_ranges']


def test_compute_distance_series_excludes_selected_index():
    df = pd.DataFrame({'x': [0.0, 3.0], 'y': [0.0, 4.0]})
    row = df.iloc[0]
    d = compute_distance_series(df, row)
    # distance to itself is inf, to (3,4) is 5
    assert np.isinf(d.iloc[0])
    assert np.isclose(d.iloc[1], 5.0)

