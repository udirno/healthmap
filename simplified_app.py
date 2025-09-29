import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# Enhanced page configuration
st.set_page_config(
    page_title="Music Explorer Map",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simplified CSS styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin: 0.5rem 0 0 0;
    }
    
    .track-card {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .track-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin: 0 0 0.5rem 0;
    }
    
    .track-artist {
        font-size: 1rem;
        color: #666;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem 0.2rem 0.2rem 0;
        display: inline-block;
    }

    .track-card:hover { 
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 10px; padding: 0.5rem 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 6px 16px rgba(102,126,234,0.3);
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 10px 24px rgba(102,126,234,0.45); }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load dataset with priority: session > real file > enhanced > embedded. Not cached to reflect in-session changes."""
    def _normalize(df_in: pd.DataFrame) -> pd.DataFrame:
        df_local = df_in.copy()
        if 'genre' not in df_local.columns:
            df_local['genre'] = 'unknown'
        return df_local

    if 'session_df' in st.session_state and st.session_state['session_df'] is not None:
        return _normalize(st.session_state['session_df'])

    real_path = 'data/spotify_tracks_real.csv'
    enhanced_path = 'data/spotify_tracks_enhanced.csv'
    fallback_path = 'data/spotify_tracks_embedded.csv'
    try:
        try:
            df = pd.read_csv(real_path)
            st.success("✅ Real dataset loaded (spotify_tracks_real.csv)")
            return _normalize(df)
        except FileNotFoundError:
            df = pd.read_csv(enhanced_path)
            st.success("✅ Enhanced dataset loaded successfully!")
            return _normalize(df)
    except FileNotFoundError:
        st.warning("⚠️ Enhanced dataset not found, loading original dataset...")
        try:
            return _normalize(pd.read_csv(fallback_path))
        except FileNotFoundError:
            st.error("❌ No dataset found! Please ensure data files are present.")
            st.stop()

def create_visualization(df, selected_genres, feature_filters):
    """Create the main visualization."""
    # Apply filtering
    filtered_df = df[df['genre'].isin(selected_genres)].copy()
    
    for feature, (min_val, max_val) in feature_filters.items():
        filtered_df = filtered_df[
            filtered_df[feature].between(min_val, max_val)
        ]
    
    # Dynamic color mapping per present genres for readability
    def _get_color_map(genres):
        palette = (
            px.colors.qualitative.Set3
            + px.colors.qualitative.Set2
            + px.colors.qualitative.Pastel
            + px.colors.qualitative.Bold
        )
        mapping = {}
        for i, g in enumerate(genres):
            mapping[g] = palette[i % len(palette)]
        return mapping
    present_genres = list(filtered_df['genre'].dropna().unique())
    color_map = _get_color_map(present_genres)
    
    # Create plot
    fig = go.Figure()
    
    for genre in selected_genres:
        genre_data = filtered_df[filtered_df['genre'] == genre]
        
        fig.add_trace(go.Scatter(
            x=genre_data['x'],
            y=genre_data['y'],
            mode='markers',
            name=genre.title(),
            marker=dict(
                color=color_map.get(genre, '#8E8E93'),
                size=10,
                opacity=0.8,
                line=dict(width=1, color='white')
            ),
            hovertemplate=
                '<b>%{customdata[0]}</b><br>' +
                'Artist: %{customdata[1]}<br>' +
                'Genre: %{customdata[2]}<br>' +
                'Energy: %{customdata[3]:.2f}<br>' +
                'Danceability: %{customdata[4]:.2f}<br>' +
                'Valence: %{customdata[5]:.2f}' +
                '<extra></extra>',
            customdata=genre_data[['track_name', 'artist_name', 'genre', 
                                 'energy', 'danceability', 'valence']].values
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'🎵 Music Similarity Space ({len(filtered_df)} tracks)',
            'font': {'size': 24},
            'x': 0.5
        },
        xaxis_title="Audio Feature Dimension 1",
        yaxis_title="Audio Feature Dimension 2",
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig, filtered_df

def simple_recommendations(df, selected_track_name, n_recommendations=5):
    """Simple recommendation system using Euclidean distance."""
    if not selected_track_name:
        return
    
    # Find the selected track
    selected_track = df[df['track_name'] == selected_track_name]
    if selected_track.empty:
        st.warning("Track not found")
        return
    
    selected_track = selected_track.iloc[0]

    # Calculate distances in 2D space robustly (avoid pandas ufunc issues)
    try:
        coords = df[['x', 'y']].astype(float).to_numpy()
        selected_xy = selected_track[['x', 'y']].astype(float).to_numpy()
        distances = np.linalg.norm(coords - selected_xy, axis=1)
    except Exception:
        # Fallback: coerce with NaNs handled
        coords = df[['x', 'y']].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy()
        selected_xy = selected_track[['x', 'y']].apply(pd.to_numeric, errors='coerce').fillna(0.0).to_numpy()
        distances = np.linalg.norm(coords - selected_xy, axis=1)
    
    # Get closest tracks (excluding the selected track)
    similar_indices = distances.nsmallest(n_recommendations + 1).index[1:]
    recommendations = df.iloc[similar_indices]
    
    st.markdown("### 🎯 Similar Tracks")
    
    for _, track in recommendations.iterrows():
        similarity = 1 / (1 + distances.iloc[track.name])
        
        st.markdown(f"""
        <div class="track-card">
            <div class="track-title">{track['track_name']}</div>
            <div class="track-artist">{track['artist_name']} • {track['genre'].title()}</div>
            <div>
                <span class="feature-badge">Energy: {track['energy']:.2f}</span>
                <span class="feature-badge">Danceability: {track['danceability']:.2f}</span>
                <span class="feature-badge">Valence: {track['valence']:.2f}</span>
                <span class="feature-badge">Similarity: {similarity:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_genre_distribution(filtered_df):
    """Display genre distribution chart."""
    if filtered_df.empty:
        st.warning("No data to display")
        return
    
    genre_counts = filtered_df['genre'].value_counts()
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=genre_counts.index,
            y=genre_counts.values,
            marker=dict(
                color=['#007AFF', '#FF3B30', '#FF9500', '#AF52DE', '#34C759'][:len(genre_counts)],
                opacity=0.8
            ),
            text=genre_counts.values,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='📊 Genre Distribution',
        xaxis_title="Genre",
        yaxis_title="Number of Tracks",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.title("🎵 Music Explorer Map")
    st.markdown("**Discover musical relationships through interactive visualization**")
    
    # Load data
    df = load_data()
    
    # Tabs for navigation
    tab_explore, tab_readme, tab_data = st.tabs(["Explore", "Tech README", "Data Guide"])

    with tab_explore:
        # Sidebar controls specific to Explore
        with st.sidebar:
            st.header("🎛️ Controls")
            st.caption("Use the sliders to filter the musical space. Hover points to inspect tracks.")
            
            # Genre selection
            selected_genres = st.multiselect(
                "🎭 Select Genres",
                options=sorted(df['genre'].unique()),
                default=sorted(df['genre'].unique()),
                help="Choose which genres to display on the map"
            )
            
            st.markdown("---")
            
            # Feature filters
            st.markdown("### 🎚️ Audio Features")
            feature_filters = {}
            
            feature_filters['energy'] = st.slider(
                "⚡ Energy", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="Perceived intensity and activity; higher = louder, faster, more aggressive"
            )
            
            feature_filters['danceability'] = st.slider(
                "💃 Danceability", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="How suitable a track is for dancing based on tempo, rhythm stability, beat strength"
            )
            
            feature_filters['valence'] = st.slider(
                "😊 Valence", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="Musical positivity; higher = happier/bright, lower = sadder/darker"
            )
            
            st.markdown("---")
            
            # Track selection for recommendations (based on filtered data)
            st.markdown("### 🎯 Track Selection")
        
        # Guard
        if 'selected_genres' not in locals() or not selected_genres:
            st.warning("⚠️ Please select at least one genre to begin exploration")
            return

        # Create visualization and filtered set
        fig, filtered_df = create_visualization(df, selected_genres, feature_filters)

        # Sidebar content that depends on filtered_df
        with st.sidebar:
            if filtered_df.empty:
                st.info("No tracks match the current filters.")
                selected_track_name = ""
            else:
                track_options = filtered_df['track_name'].tolist()
                selected_track_name = st.selectbox(
                    "Select a track for recommendations",
                    options=[""] + track_options,
                    help="Choose a track to see similar recommendations"
                )

        # Display main plot with brief explainer
        with st.expander("What am I looking at?", expanded=True):
            st.markdown("""
            - **Each dot is a track**; distance ≈ acoustic similarity from the 2D embedding.
            - **Colors are genres/tags**; new tags get auto colors.
            - **Sliders change the cohort**: e.g., higher danceability biases toward steady rhythm, strong beats; higher energy biases toward louder, faster tracks; higher valence biases toward brighter/happier mood.
            - **Select a track** to see nearest neighbors in this filtered space.
            """)
        # Compact genre legend with counts
        if not filtered_df.empty:
            gcounts = filtered_df['genre'].value_counts()
            chips = " ".join([f"<span class='feature-badge'>{g}: {gcounts[g]}</span>" for g in gcounts.index])
            st.markdown(chips, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)

        # Statistics dashboard
        st.markdown("### 📊 Statistics Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(filtered_df)}</div>
                <div class="metric-label">Total Tracks</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(filtered_df['genre'].unique())}</div>
                <div class="metric-label">Genres</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_energy = filtered_df['energy'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_energy:.2f}</div>
                <div class="metric-label">Avg Energy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_valence = filtered_df['valence'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_valence:.2f}</div>
                <div class="metric-label">Avg Valence</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Supporting charts (succinct)
        st.markdown("### 📊 Supporting Views")
        cA, cB = st.columns([2,2])
        with cA:
            st.caption("Number of tracks by genre in the current filters")
            display_genre_distribution(filtered_df)
        with cB:
            if not filtered_df.empty:
                means = filtered_df[['danceability','energy','valence','acousticness','instrumentalness','liveness','speechiness']].mean()
                fig_f = go.Figure(data=[go.Bar(x=means.index, y=means.values, marker_color="#667eea")])
                fig_f.update_layout(height=320, margin=dict(t=40,b=40,l=20,r=20), title_text="Feature Means (filtered)")
                st.plotly_chart(fig_f, use_container_width=True)
                st.caption("Average feature intensities for the filtered set (0-1 scale)")
        
        # Recommendations (use filtered_df for neighborhood)
        if selected_track_name:
            st.markdown("#### Recommendations based on your selected track")
            simple_recommendations(filtered_df, selected_track_name)
        
        # Sample tracks
        st.markdown("### 🎵 Sample Tracks")
        if not filtered_df.empty:
            sample_tracks = filtered_df.sample(min(5, len(filtered_df)))
            for _, track in sample_tracks.iterrows():
                st.markdown(f"""
                <div class="track-card">
                    <div class="track-title">{track['track_name']}</div>
                    <div class="track-artist">{track['artist_name']} • {track['genre'].title()}</div>
                    <div>
                        <span class="feature-badge">Energy: {track['energy']:.2f}</span>
                        <span class="feature-badge">Danceability: {track['danceability']:.2f}</span>
                        <span class="feature-badge">Valence: {track['valence']:.2f}</span>
                        <span class="feature-badge">Acousticness: {track['acousticness']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_readme:
        st.header("🧪 Tech README: Music Explorer")
        st.markdown("""
        - **Stack**: Streamlit + Plotly, scikit-learn/UMAP pipeline (authored in Python, iterated with Cursor).
        - **Goal**: Visualize musical similarity. Each dot is a track; proximity ≈ acoustic similarity.
        - **Data**: 9D features (energy, danceability, valence, acousticness, instrumentalness, liveness, speechiness, tempo, loudness). Embedded to 2D via UMAP.
        - **UMAP**: Preserves local neighborhoods from high-dim to 2D. Think: "Who are my nearest neighbors if we squeeze space intelligently?"
        - **Similarity**: In this simplified app, nearest neighbors are computed in 2D (fast, intuitive). The enhanced app supports KNN on scaled multi-feature vectors for higher fidelity.
        - **Filters**: Sliders apply range constraints server-side; all cards, charts, and recommendations reflect the filtered subset.
        - **Real Data**: If `data/spotify_tracks_real.csv` is present with the same schema, it is loaded automatically.
        - **What’s next**: Artist-level genres (fallback), tag fusion (Last.fm/MusicBrainz), or shallow genre classifiers over features.
        """)

    with tab_data:
        st.header("📦 Bring Your Own Data")
        st.markdown("""
        **What the app needs** (columns):
        - `track_id` (string, unique)
        - `track_name` (string)
        - `artist_name` (string)
        - `genre` (string, optional)
        - Features in [0,1]: `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `liveness`, `speechiness`
        - Numeric: `tempo` (BPM), `loudness` (dB), and 2D embedding `x`, `y`

        **Don’t have genres?** That’s fine: you can still explore. Later we can:
        - infer genres via artist tags (Last.fm/MusicBrainz),
        - cluster and label groups,
        - or use a lightweight classifier on features.

        **Where to get data** (practical options):
        - Spotify Web API `audio_features` for tracks/playlists (IDs from your library or playlist export)
        - Public datasets (e.g., Kaggle Spotify Tracks) with audio features
        - Your Spotify account export + script to fetch `audio_features` by track IDs
        """)

        # Template download
        import io
        def _template_df():
            return pd.DataFrame([
                {
                    'track_id': 'id_001', 'track_name': 'Song A', 'artist_name': 'Artist X', 'genre': 'pop',
                    'danceability': 0.72, 'energy': 0.68, 'valence': 0.55, 'acousticness': 0.12,
                    'instrumentalness': 0.00, 'liveness': 0.10, 'speechiness': 0.05,
                    'tempo': 120.0, 'loudness': -6.5, 'x': 3.21, 'y': 1.45
                },
                {
                    'track_id': 'id_002', 'track_name': 'Song B', 'artist_name': 'Artist Y', 'genre': 'rock',
                    'danceability': 0.45, 'energy': 0.82, 'valence': 0.40, 'acousticness': 0.05,
                    'instrumentalness': 0.01, 'liveness': 0.12, 'speechiness': 0.04,
                    'tempo': 140.0, 'loudness': -5.2, 'x': -2.10, 'y': 0.88
                }
            ])

        buf = io.StringIO()
        _template_df().to_csv(buf, index=False)
        st.download_button(
            label="⬇️ Download CSV Template",
            data=buf.getvalue(),
            file_name="music_explorer_template.csv",
            mime="text/csv"
        )

        st.markdown("---")
        st.subheader("Quick Validator (optional)")
        uploaded = st.file_uploader("Upload a CSV to validate schema or use it now", type=["csv"]) 

        required_cols = [
            'track_id','track_name','artist_name',
            'danceability','energy','valence','acousticness','instrumentalness','liveness','speechiness',
            'tempo','loudness','x','y'
        ]

        if uploaded is not None:
            try:
                df_u = pd.read_csv(uploaded)
                missing = [c for c in required_cols if c not in df_u.columns]
                if missing:
                    st.error(f"Missing required columns: {missing}")
                else:
                    # basic range checks
                    feature_cols = ['danceability','energy','valence','acousticness','instrumentalness','liveness','speechiness']
                    bad_ranges = []
                    for c in feature_cols:
                        if not ((df_u[c] >= 0).all() and (df_u[c] <= 1).all()):
                            bad_ranges.append(c)
                    if bad_ranges:
                        st.warning(f"These feature columns should be in [0,1]: {bad_ranges}")
                    else:
                        st.success("Schema looks good.")
                        st.dataframe(df_u.head())
                        if st.button("Use this CSV now (session)"):
                            st.session_state['session_df'] = df_u
                            st.toast("Dataset loaded for this session. Open the Explore tab.")
                            st.success("Using uploaded dataset for this session. Redirecting to Explore...")
                            st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to read/validate CSV: {e}")

        st.markdown("---")
        st.subheader("No API key? Generate a real playlist CSV")
        st.markdown("""
        We can fetch real tracks from the free **iTunes Search API** (no API key) based on a prompt, then approximate features and embed them on the map. This is a pragmatic placeholder until you provide true audio features.
        """)

        import requests
        import time

        with st.form("itunes_generator"):
            colg1, colg2 = st.columns(2)
            with colg1:
                query = st.text_input("Describe the vibe/seed (artist/genre/mood)", value="chill electronic")
                country = st.selectbox("Store country", options=["US","GB","CA","DE","FR","JP","AU"], index=0)
            with colg2:
                limit = st.slider("Number of tracks", 10, 50, 25, 5)
                seed_variability = st.slider("Feature variability", 0.05, 0.50, 0.20, 0.05, help="Higher = more diverse synthetic features")
            generate_clicked = st.form_submit_button("Generate CSV from iTunes")

        def _approx_features(seed: float, n: int):
            rng = np.random.default_rng(int(seed))
            base = {
                'danceability': rng.uniform(0.4, 0.8, n),
                'energy': rng.uniform(0.3, 0.9, n),
                'valence': rng.uniform(0.2, 0.8, n),
                'acousticness': rng.uniform(0.0, 0.7, n),
                'instrumentalness': rng.uniform(0.0, 0.6, n),
                'liveness': rng.uniform(0.05, 0.4, n),
                'speechiness': rng.uniform(0.02, 0.2, n),
                'tempo': rng.uniform(80, 160, n),
                'loudness': rng.uniform(-12, -3, n)
            }
            # add controllable variability
            for k in ['danceability','energy','valence','acousticness','instrumentalness','liveness','speechiness']:
                noise = rng.normal(0, seed_variability/3, n)
                base[k] = np.clip(base[k] + noise, 0.0, 1.0)
            return base

        def _simple_embed(xy_seed: float, features_df: pd.DataFrame):
            rng = np.random.default_rng(int(xy_seed))
            # Fast placeholder: project two principal-like composites
            x = (
                0.6*features_df['danceability'] + 0.7*features_df['energy']
                - 0.3*features_df['acousticness'] + rng.normal(0, 0.2, len(features_df))
            ) * 5
            y = (
                0.6*features_df['valence'] + 0.4*features_df['danceability']
                - 0.4*features_df['liveness'] + rng.normal(0, 0.2, len(features_df))
            ) * 5
            return x, y

        if generate_clicked:
            try:
                params = {"term": query, "entity": "song", "limit": int(limit), "country": country}
                r = requests.get("https://itunes.apple.com/search", params=params, timeout=10)
                r.raise_for_status()
                results = r.json().get("results", [])
                if not results:
                    st.warning("No results from iTunes. Try a different query.")
                else:
                    track_rows = []
                    for rec in results:
                        track_rows.append({
                            'track_id': f"itunes_{rec.get('trackId','na')}",
                            'track_name': rec.get('trackName','Unknown'),
                            'artist_name': rec.get('artistName','Unknown'),
                            'genre': rec.get('primaryGenreName','unknown').lower()
                        })
                    meta_df = pd.DataFrame(track_rows)
                    feat = _approx_features(seed=time.time(), n=len(meta_df))
                    feat_df = pd.DataFrame(feat)
                    x, y = _simple_embed(xy_seed=time.time(), features_df=feat_df)
                    out_df = pd.concat([meta_df, feat_df], axis=1)
                    out_df['x'] = x
                    out_df['y'] = y

                    # Preview
                    st.success(f"Generated {len(out_df)} tracks from iTunes (with approximated features)")
                    st.dataframe(out_df.head())

                    # Offer as download or set as session dataset
                    buf2 = io.StringIO()
                    out_df.to_csv(buf2, index=False)
                    st.download_button("⬇️ Download Generated CSV", data=buf2.getvalue(), file_name="itunes_generated_tracks.csv", mime="text/csv")

                    if st.button("Use this dataset in the app now"):
                        st.session_state['session_df'] = out_df
                        st.toast("Dataset loaded for this session. Open the Explore tab.")
                        st.success("This session will now use the generated dataset. Redirecting to Explore...")
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")

if __name__ == "__main__":
    main()
