# 🎵 Music Explorer Map

**Interactive Audio Feature Visualization** - Discover musical relationships through machine learning and 2D projection.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd music-explorer
python3 -m venv .venv --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
. .venv/bin/activate && python get-pip.py
pip install -r requirements.txt
streamlit run simplified_app.py
```

**Open**: http://localhost:8501

## 🌟 What This Does

- **Interactive Map**: Visualize music similarity in 2D space
- **Smart Recommendations**: Find similar tracks based on audio features  
- **Real Data**: Generate datasets using iTunes Search API (no auth needed)
- **Educational**: Learn about ML, dimensionality reduction, and music analysis
- **Apple-Inspired UI**: Clean, modern interface with hover effects

## 📚 Documentation

- **[Project Context](docs/CONTEXT.md)** - Current state, known issues, technical decisions
- **[Development Roadmap](docs/ROADMAP.md)** - Next features and priorities  
- **[Data Guide](docs/DATA_GUIDE.md)** - How to get and format music data
- **[Test Plan](docs/TEST_PLAN.md)** - Manual testing checklist

## ✅ Recent Improvements

- Fixed numpy distance error in recommendations
- Auto-switch to Explore after adopting a dataset (CSV or iTunes)
- Distinct, consistent genre colors across views
- Guided presets and radar chart for better education/UX
- Shareable links via URL parameters (genres and slider ranges)

## 🎛️ How to Use

1. **Explore Tab**: Adjust sliders to filter tracks, select points for recommendations
2. **Data Guide Tab**: Generate real music data or upload your own CSV
3. **Tech README Tab**: Learn about the ML concepts and architecture

## 📊 Dataset

The application uses synthetic audio feature data with realistic metadata:

- **800 tracks** across 5 genres (electronic, classical, jazz, pop, rock)
- **9-dimensional audio features**: energy, danceability, valence, acousticness, instrumentalness, liveness, speechiness, tempo, loudness
- **2D UMAP embedding**: Preserves acoustic similarity relationships
- **Authentic naming**: Generated realistic track and artist names

### Data Files
- `data/spotify_tracks_enhanced.csv` - Main dataset with realistic metadata
- `data/spotify_tracks_embedded.csv` - Original dataset with synthetic names
- `data/spotify_tracks_raw.csv` - Raw audio features before UMAP

## 🎛️ Usage Guide

### Main Interface
1. **Genre Selection**: Choose which genres to display on the map
2. **Feature Filters**: Adjust sliders to filter tracks by audio characteristics
3. **Track Selection**: Select a track to see similar recommendations
4. **Interactive Plot**: Click and hover on points for detailed information

### Key Features
- **Similarity Recommendations**: Select any track to see 5 most similar tracks
- **Spatial Clusters**: View auto-generated playlists based on acoustic clustering
- **Genre Distribution**: See the breakdown of tracks by genre
- **Statistics Dashboard**: Real-time metrics for filtered data

## 🔧 Technical Architecture

### Backend Components
- **UMAP**: Dimensionality reduction preserving local and global structure
- **scikit-learn**: KNN recommendations and K-means clustering
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

### Frontend Components
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Custom CSS**: Apple Music-inspired styling

### Machine Learning Pipeline
1. **Feature Extraction**: 9-dimensional audio feature vectors
2. **Standardization**: Normalize features for consistent scaling
3. **UMAP Embedding**: Reduce to 2D while preserving similarity
4. **KNN Model**: Find similar tracks based on feature space
5. **Clustering**: Group tracks into acoustic playlists

## 📁 Project Structure

```
music-explorer/
├── data/                           # Dataset files
│   ├── spotify_tracks_enhanced.csv    # Main dataset (realistic names)
│   ├── spotify_tracks_embedded.csv    # Original dataset (synthetic names)
│   └── spotify_tracks_raw.csv         # Raw audio features
├── src/                            # Source code modules
│   ├── preprocessing.py               # UMAP computation
│   ├── visualization.py              # Plot generation
│   └── data_collection.py            # Data generation utilities
├── notebooks/                      # Jupyter notebooks
│   ├── 01_data_collection.ipynb      # Data generation
│   ├── 02_dimensionality_reduction.ipynb  # UMAP analysis
│   └── 03_interactive_visualization.ipynb # Visualization
├── streamlit_app.py               # Basic Streamlit interface
├── enhanced_streamlit_app.py       # Enhanced interface (recommended)
├── enhanced_data_generator.py     # Metadata enhancement utility
├── test_app.py                    # Application test suite
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
pytest -q
```

This will test:
- Data loading functionality
- KNN model creation
- Clustering algorithm
- Recommendation system

## 🎨 Customization

### Adding New Genres
1. Update `enhanced_data_generator.py` with new genre vocabulary
2. Regenerate the enhanced dataset
3. Update color mappings in the visualization code

### Modifying Visualizations
- Edit `enhanced_streamlit_app.py` for UI changes
- Modify `src/visualization.py` for plot customization
- Update CSS styling for different aesthetics

### Extending Features
- Add new audio features in `src/preprocessing.py`
- Implement additional ML models for recommendations
- Create new clustering algorithms

## 🐛 Troubleshooting

### Common Issues

1. **"No dataset found" error**
   - Ensure data files are in the `data/` directory
   - Run `enhanced_data_generator.py` if enhanced dataset is missing

2. **CSS styling not applying**
   - Clear browser cache
   - Check browser console for errors
   - Ensure Streamlit version compatibility

3. **Recommendations not working**
   - Verify track selection is working
   - Check that KNN model is properly initialized
   - Ensure feature columns match between model and data

4. **Performance issues**
   - Reduce number of tracks in dataset
   - Adjust UMAP parameters for faster computation
   - Use caching for expensive operations

### Getting Help

- Check the test suite output for specific errors
- Review the console output when running Streamlit
- Ensure all dependencies are properly installed

## 📈 Future Enhancements

- **Real Spotify Integration**: Connect to Spotify API for authentic data
- **Audio Preview**: Add 30-second track previews
- **Playlist Export**: Export clusters as Spotify playlists
- **Advanced ML**: Implement collaborative filtering
- **Mobile Responsiveness**: Optimize for mobile devices
- **User Authentication**: Save user preferences and playlists

## 📄 License

This project is for educational and demonstration purposes. Feel free to use and modify for your own projects.

## 🙏 Acknowledgments

- **UMAP**: For dimensionality reduction algorithm
- **Streamlit**: For the web application framework
- **Plotly**: For interactive visualizations
- **scikit-learn**: For machine learning algorithms

---

**Happy Music Exploring! 🎵**