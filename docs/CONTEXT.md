# Music Explorer Map - Project Context

## Current State (v1.0.0)
**Status**: Working demo with known issues  
**Last Updated**: September 2024

### Architecture
- **Backend**: Python 3.12.2, Streamlit, Plotly, Pandas, NumPy
- **Data Processing**: UMAP dimensionality reduction (avoided due to TensorFlow compatibility issues)
- **Frontend**: Streamlit with custom CSS (Apple Music-inspired)
- **Data Sources**: iTunes Search API (no auth required), CSV upload, synthetic fallback

### Key Files
- `simplified_app.py` - **Main application** (working, no TensorFlow deps)
- `enhanced_streamlit_app.py` - Advanced version (broken due to TensorFlow/AVX issues)
- `data/spotify_tracks_enhanced.csv` - Realistic track names
- `data/spotify_tracks_embedded.csv` - Original synthetic data

### Current Features
✅ **Working**:
- Interactive 2D music similarity map
- Genre filtering with dynamic color mapping
- Feature sliders (Energy, Danceability, Valence) with tooltips
- iTunes Search API data generator
- CSV upload with schema validation
- Session state management
- Recommendations based on 2D Euclidean distance
- Educational "Tech README" tab

❌ **Known Issues**:
1. **Critical Bug**: `TypeError: loop of ufunc does not support argument 0 of type numpy.float64` in `simple_recommendations()` (line 214)
2. **UX Issue**: "Use this dataset in the app now" doesn't auto-switch to Explore tab
3. **Data Flow**: Upload/generate → use now → manual tab switch required
4. **Visual**: New genres from iTunes don't get distinct colors initially

### Technical Decisions Made
- **Avoided TensorFlow**: Created `simplified_app.py` to avoid AVX instruction compatibility issues
- **Simple Recommendations**: Using 2D Euclidean distance instead of full feature space KNN
- **Session State**: `st.session_state['session_df']` for dynamic data switching
- **No Caching**: Removed `@st.cache_data` to allow real-time data updates

### Data Schema Requirements
```csv
track_id,artist_name,track_name,genre,energy,danceability,valence,x,y
```

### Next Priority Fixes
1. Fix the numpy sqrt error in recommendations
2. Auto-redirect to Explore after "Use now"
3. Improve upload responsiveness
4. Add guided presets (Chill, High-Energy, etc.)
5. Replace feature means bar with radar chart

### Development Environment
- Python 3.12.2 (conda-forge)
- macOS (darwin 24.6.0)
- Streamlit ports: 8502, 8503, 8520 (multiple instances running)

### How to Run
```bash
cd /Users/udirno/Downloads/music-explorer
pip install -r requirements.txt
streamlit run simplified_app.py
```

### For Next Agent
- Start with `simplified_app.py` (the working version)
- Fix the numpy error first, then enhance UX
- Check `docs/ROADMAP.md` for detailed next steps
- Test with iTunes generator and CSV upload flows
