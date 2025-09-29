import pandas as pd
import numpy as np
import plotly.express as px


def get_color_map(genres: list[str]) -> dict[str, str]:
    """Return a deterministic genre -> color mapping using Plotly qualitative palettes.

    The order of provided genres determines assignment, stable across views.
    """
    palette = (
        px.colors.qualitative.Set3
        + px.colors.qualitative.Set2
        + px.colors.qualitative.Pastel
        + px.colors.qualitative.Bold
        + px.colors.qualitative.Safe
    )
    mapping: dict[str, str] = {}
    for i, g in enumerate(genres):
        mapping[g] = palette[i % len(palette)]
    return mapping


REQUIRED_COLUMNS = [
    'track_id', 'track_name', 'artist_name', 'genre',
    'danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness',
    'tempo', 'loudness', 'x', 'y'
]

RANGED_FEATURES_01 = [
    'danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness'
]


def validate_schema(df: pd.DataFrame) -> dict:
    """Validate dataset schema and ranges.

    Returns a report dict with keys: ok (bool), missing (list), bad_ranges (list), notes (list).
    """
    report = {"ok": True, "missing": [], "bad_ranges": [], "notes": []}
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        report["ok"] = False
        report["missing"] = missing
        return report

    # Coerce numeric columns where applicable
    for c in RANGED_FEATURES_01 + ['tempo', 'loudness', 'x', 'y']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    bad_ranges = []
    for c in RANGED_FEATURES_01:
        series = df[c]
        if not ((series >= 0).all() and (series <= 1).all()):
            bad_ranges.append(c)
    if bad_ranges:
        report["ok"] = False
        report["bad_ranges"] = bad_ranges
    return report


def compute_distance_series(df_xy: pd.DataFrame, selected_row: pd.Series) -> pd.Series:
    """Compute Euclidean distances in 2D from selected_row to each row in df_xy.

    Returns a Pandas Series aligned to df_xy.index. Selected row index is set to np.inf.
    """
    coords = df_xy[['x', 'y']].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy()
    selected_xy = selected_row[['x', 'y']].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy()
    distances_arr = np.linalg.norm(coords - selected_xy, axis=1)
    distances = pd.Series(distances_arr, index=df_xy.index)
    if selected_row.name in distances.index:
        distances.loc[selected_row.name] = np.inf
    return distances

