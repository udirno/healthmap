# Data Guide - Music Explorer Map

## Required Schema
Your CSV must have these exact columns:
```csv
track_id,artist_name,track_name,genre,energy,danceability,valence,x,y
```

### Column Descriptions
- `track_id`: Unique identifier (string)
- `artist_name`: Artist name (string)
- `track_name`: Song title (string)
- `genre`: Music genre (string)
- `energy`: Energy level 0.0-1.0 (float)
- `danceability`: Danceability 0.0-1.0 (float)
- `valence`: Positivity/positivity 0.0-1.0 (float)
- `x`: 2D projection X coordinate (float)
- `y`: 2D projection Y coordinate (float)

## Data Sources

### 1. iTunes Search API (Built-in Generator)
- **Access**: No API key required
- **Usage**: Use the "Data Guide" tab in the app
- **Limitations**: 
  - Synthetic audio features (not real Spotify data)
  - Approximate 2D coordinates
  - Limited to 50 tracks per search

### 2. Spotify Web API (Deprecated)
- **Status**: Genre endpoints deprecated
- **Alternative**: Use track features, classify genres separately
- **Note**: Requires authentication

### 3. Last.fm API
- **Access**: Free tier available
- **Features**: Genre tags, similar artists
- **Limitation**: No audio features

### 4. MusicBrainz
- **Access**: Free, no API key
- **Features**: Metadata, relationships
- **Limitation**: No audio features

## Getting Real Data

### Option A: Use Built-in Generator
1. Go to "Data Guide" tab
2. Enter search query (e.g., "rock hits 2023")
3. Click "Generate Dataset"
4. Review and click "Use this dataset in the app now"

### Option B: Upload Your Own CSV
1. Prepare CSV with required schema
2. Go to "Data Guide" tab
3. Upload file
4. Click "Use this dataset in the app now"

### Option C: Create from Spotify Data
1. Export your Spotify data (if available)
2. Use external tools to extract audio features
3. Apply UMAP for 2D projection
4. Format as required CSV

## Data Quality Tips
- **Genres**: Use consistent naming (e.g., "rock", not "Rock" or "ROCK")
- **Features**: Ensure values are 0.0-1.0 range
- **Coordinates**: X,Y should be reasonable 2D coordinates (not too extreme)
- **Size**: 50-500 tracks work well for visualization

## Sample Data
See `data/sample_real.csv` for a minimal example.

## Troubleshooting
- **Schema Error**: Check column names and types
- **Empty Map**: Verify X,Y coordinates are numeric
- **No Colors**: Ensure genre column has values
- **Slow Loading**: Reduce dataset size

## Future Improvements
- Auto-feature extraction from audio files
- Real-time Spotify integration
- Genre classification using ML
- Batch processing for large datasets
