# Music Explorer Map - Development Roadmap

## Immediate Fixes (Priority 1)
### 1. Fix Critical Bug
- **Issue**: `TypeError: loop of ufunc does not support argument 0 of type numpy.float64` in `simple_recommendations()`
- **Location**: `simplified_app.py:214`
- **Fix**: Replace `distances.iloc[track.name]` with `distances[track.name]` and ensure proper numpy operations
- **Impact**: App crashes when viewing recommendations

### 2. Improve Data Flow UX
- **Issue**: "Use this dataset in the app now" doesn't auto-switch to Explore tab
- **Solution**: Add `st.experimental_rerun()` and query params or consolidate UI
- **Impact**: Confusing user experience

### 3. Upload Responsiveness
- **Issue**: CSV upload feels slow and unresponsive
- **Solution**: Add progress indicators and success feedback
- **Impact**: User confidence

## Enhancement Features (Priority 2)
### 4. Guided Presets
- **Feature**: Add preset buttons (Chill, High-Energy, Happy, Acoustic)
- **Implementation**: Set slider ranges to teach feature effects
- **Location**: Sidebar in Explore tab

### 5. Visual Improvements
- **Replace**: Feature means bar chart with interactive radar chart
- **Add**: Legend panel with color swatches and genre toggles
- **Enhance**: Hover animations and micro-interactions

### 6. Educational Content
- **Add**: Scrollytelling narrative that highlights changes as sliders adjust
- **Expand**: "What am I looking at?" section with more ML concepts
- **Include**: UMAP explanation and why 2D projection works

## Advanced Features (Priority 3)
### 7. Real Data Integration
- **Goal**: Replace synthetic data with real music datasets
- **Sources**: Spotify Web API (when available), Last.fm, MusicBrainz
- **Challenge**: Genre classification (Spotify API deprecated)

### 8. Advanced Recommendations
- **Upgrade**: From 2D distance to full feature space KNN
- **Add**: Collaborative filtering
- **Include**: Playlist generation from clusters

### 9. Performance & Scale
- **Optimize**: Large dataset handling
- **Add**: Caching for expensive operations
- **Implement**: Progressive loading

## Technical Debt
- **Refactor**: Split `simplified_app.py` into modules
- **Add**: Comprehensive error handling
- **Improve**: Code documentation and type hints
- **Test**: Add unit tests for core functions

## Success Metrics
- **User Engagement**: Time spent exploring, slider interactions
- **Educational Value**: User understanding of ML concepts
- **Data Quality**: Real vs synthetic data usage
- **Performance**: Load times, responsiveness

## Notes for Next Agent
- Start with Priority 1 fixes - they're blocking basic functionality
- Test thoroughly with iTunes generator and CSV upload
- Maintain the Apple Music aesthetic
- Keep educational focus - this is a learning tool
- Document decisions in `docs/CONTEXT.md`
