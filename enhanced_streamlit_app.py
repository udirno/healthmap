import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# Enhanced page configuration
st.set_page_config(
    page_title="Music Explorer Map",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/music-explorer',
        'Report a bug': 'https://github.com/your-repo/music-explorer/issues',
        'About': "Music Explorer Map - Interactive Audio Feature Visualization"
    }
)

# Enhanced CSS styling with proper Apple Music aesthetic
st.markdown("""
<style>
    /* Import Apple system fonts */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem 1rem;
    }
    
    /* Control sections */
    .control-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .control-section h3 {
        color: #333;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e1e5e9;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Slider styling */
    .stSlider > div > div {
        border-radius: 12px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Chart container styling */
    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Track card styling */
    .track-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .track-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .track-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin: 0 0 0.5rem 0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .track-artist {
        font-size: 1rem;
        color: #666;
        margin: 0 0 1rem 0;
        font-weight: 500;
    }
    
    .track-features {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Genre distribution chart styling */
    .genre-chart {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .track-features {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_enhanced_data():
    """Load enhanced dataset with authentic metadata."""
    try:
        df = pd.read_csv('data/spotify_tracks_enhanced.csv')
        st.success("✅ Enhanced dataset loaded successfully!")
        return df
    except FileNotFoundError:
        st.warning("⚠️ Enhanced dataset not found, loading original dataset...")
        try:
            return pd.read_csv('data/spotify_tracks_embedded.csv')
        except FileNotFoundError:
            st.error("❌ No dataset found! Please ensure data files are present.")
            st.stop()

@st.cache_data
def create_knn_model(df):
    """Create k-nearest neighbors model for recommendations."""
    feature_cols = ['x', 'y', 'energy', 'danceability', 'valence', 'acousticness', 'instrumentalness']
    features = df[feature_cols].values
    
    # Normalize features for better distance calculation
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Create KNN model
    knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
    knn.fit(features_scaled)
    
    return knn, scaler, feature_cols

@st.cache_data
def create_clusters(df, n_clusters=8):
    """Create spatial clusters for playlist generation."""
    feature_cols = ['x', 'y']
    features = df[feature_cols].values
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features)
    
    return clusters, kmeans

def create_modern_visualization(df, selected_genres, feature_filters, selected_track_idx=None):
    """Generate Apple Music-inspired visualization with enhanced interactivity."""
    
    # Apply comprehensive filtering
    filtered_df = df[df['genre'].isin(selected_genres)].copy()
    
    for feature, (min_val, max_val) in feature_filters.items():
        filtered_df = filtered_df[
            filtered_df[feature].between(min_val, max_val)
        ]
    
    # Modern color palette with better contrast
    color_map = {
        'electronic': '#007AFF',  # Apple Blue
        'classical': '#FF3B30',   # Apple Red
        'rock': '#FF9500',        # Apple Orange
        'jazz': '#AF52DE',        # Apple Purple
        'pop': '#34C759'          # Apple Green
    }
    
    # Create sophisticated scatter plot
    fig = go.Figure()
    
    for genre in selected_genres:
        genre_data = filtered_df[filtered_df['genre'] == genre]
        
        # Highlight selected track
        marker_size = 15 if selected_track_idx is not None else 10
        marker_opacity = 1.0 if selected_track_idx is not None else 0.8
        
        fig.add_trace(go.Scatter(
            x=genre_data['x'],
            y=genre_data['y'],
            mode='markers',
            name=genre.title(),
            marker=dict(
                color=color_map.get(genre, '#8E8E93'),
                size=marker_size,
                opacity=marker_opacity,
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            hovertemplate=
                '<b>%{customdata[0]}</b><br>' +
                'Artist: %{customdata[1]}<br>' +
                'Genre: %{customdata[2]}<br>' +
                'Energy: %{customdata[3]:.2f}<br>' +
                'Danceability: %{customdata[4]:.2f}<br>' +
                'Valence: %{customdata[5]:.2f}<br>' +
                'Acousticness: %{customdata[6]:.2f}' +
                '<extra></extra>',
            customdata=genre_data[['track_name', 'artist_name', 'genre', 
                                 'energy', 'danceability', 'valence', 'acousticness']].values
        ))
    
    # Highlight selected track if any
    if selected_track_idx is not None and selected_track_idx < len(filtered_df):
        selected_track = filtered_df.iloc[selected_track_idx]
        fig.add_trace(go.Scatter(
            x=[selected_track['x']],
            y=[selected_track['y']],
            mode='markers',
            name='Selected Track',
            marker=dict(
                color='#FF6B6B',
                size=20,
                opacity=1.0,
                line=dict(width=3, color='white'),
                symbol='star'
            ),
            showlegend=False,
            hovertemplate=f'<b>{selected_track["track_name"]}</b><br>Selected Track<extra></extra>'
        ))
    
    # Modern layout styling
    fig.update_layout(
        title={
            'text': f'🎵 Music Similarity Space ({len(filtered_df)} tracks)',
            'font': {'size': 28, 'family': 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Audio Feature Dimension 1",
        yaxis_title="Audio Feature Dimension 2",
        font={'family': 'SF Pro Text, -apple-system, BlinkMacSystemFont, sans-serif', 'size': 14},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font={'size': 16, 'family': 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'}
        ),
        margin=dict(t=100, b=80, l=80, r=80)
    )
    
    # Enhanced grid styling
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False,
        showline=True,
        linecolor='rgba(128,128,128,0.3)',
        linewidth=1
    )
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False,
        showline=True,
        linecolor='rgba(128,128,128,0.3)',
        linewidth=1
    )
    
    return fig, filtered_df

def display_track_recommendations(df, selected_track_idx, knn_model, scaler, feature_cols, n_recommendations=5):
    """Generate similarity-based recommendations using KNN."""
    if selected_track_idx is None or selected_track_idx >= len(df):
        return
    
    selected_track = df.iloc[selected_track_idx]
    
    # Prepare features for the selected track
    track_features = selected_track[feature_cols].values.reshape(1, -1)
    track_features_scaled = scaler.transform(track_features)
    
    # Find nearest neighbors
    distances, indices = knn_model.kneighbors(track_features_scaled)
    
    # Get recommendations (excluding the selected track itself)
    recommendation_indices = indices[0][1:n_recommendations+1]
    recommendations = df.iloc[recommendation_indices]
    
    st.markdown("### 🎯 Similar Tracks")
    
    for i, (_, track) in enumerate(recommendations.iterrows()):
        similarity_score = 1 / (1 + distances[0][i+1])  # Convert distance to similarity
        
        with st.container():
            st.markdown(f"""
            <div class="track-card">
                <div class="track-title">{track['track_name']}</div>
                <div class="track-artist">{track['artist_name']} • {track['genre'].title()}</div>
                <div class="track-features">
                    <span class="feature-badge">Energy: {track['energy']:.2f}</span>
                    <span class="feature-badge">Danceability: {track['danceability']:.2f}</span>
                    <span class="feature-badge">Valence: {track['valence']:.2f}</span>
                    <span class="feature-badge">Similarity: {similarity_score:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_genre_distribution(filtered_df):
    """Display enhanced genre distribution chart."""
    if filtered_df.empty:
        st.warning("No data to display")
        return
    
    genre_counts = filtered_df['genre'].value_counts()
    
    # Define colors for genres
    color_map = {
        'electronic': '#007AFF',
        'classical': '#FF3B30', 
        'rock': '#FF9500',
        'jazz': '#AF52DE',
        'pop': '#34C759'
    }
    
    # Create colors array based on actual genres present
    colors = [color_map.get(genre, '#8E8E93') for genre in genre_counts.index]
    
    # Create a more sophisticated chart
    fig = go.Figure(data=[
        go.Bar(
            x=genre_counts.index,
            y=genre_counts.values,
            marker=dict(
                color=colors,
                line=dict(color='white', width=2),
                opacity=0.8
            ),
            text=genre_counts.values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '📊 Genre Distribution',
            'font': {'size': 20, 'family': 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'},
            'x': 0.5
        },
        xaxis_title="Genre",
        yaxis_title="Number of Tracks",
        font={'family': 'SF Pro Text, -apple-system, BlinkMacSystemFont, sans-serif'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True
    )
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_cluster_playlists(df, clusters):
    """Display spatial clusters as playlists."""
    st.markdown("### 🎵 Spatial Clusters (Auto-Generated Playlists)")
    
    if len(clusters) != len(df):
        st.warning("⚠️ Cluster data mismatch with dataset")
        return
    
    unique_clusters = np.unique(clusters)
    
    for cluster_id in unique_clusters[:4]:  # Show top 4 clusters
        cluster_tracks = df[clusters == cluster_id]
        
        if len(cluster_tracks) == 0:
            continue
            
        with st.expander(f"🎶 Cluster {cluster_id + 1} ({len(cluster_tracks)} tracks)"):
            # Show cluster statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tracks", len(cluster_tracks))
            with col2:
                st.metric("Genres", len(cluster_tracks['genre'].unique()))
            with col3:
                avg_energy = cluster_tracks['energy'].mean()
                st.metric("Avg Energy", f"{avg_energy:.2f}")
            
            # Show sample tracks
            st.markdown("**Sample tracks:**")
            sample_tracks = cluster_tracks.sample(min(5, len(cluster_tracks)))
            for _, track in sample_tracks.iterrows():
                st.markdown(f"• **{track['track_name']}** by {track['artist_name']} ({track['genre']})")

def main():
    # Enhanced header section
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Music Explorer Map</h1>
        <p>Discover musical relationships through interactive visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load enhanced dataset
    df = load_enhanced_data()
    
    # Create models
    knn_model, scaler, feature_cols = create_knn_model(df)
    clusters, kmeans_model = create_clusters(df)
    
    # Sidebar controls with enhanced styling
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
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
            help="Musical energy and intensity"
        )
        
        feature_filters['danceability'] = st.slider(
            "💃 Danceability", 0.0, 1.0, (0.0, 1.0), 0.05,
            help="Rhythmic suitability for dancing"
        )
        
        feature_filters['valence'] = st.slider(
            "😊 Valence", 0.0, 1.0, (0.0, 1.0), 0.05,
            help="Musical positivity and mood"
        )
        
        feature_filters['acousticness'] = st.slider(
            "🎸 Acousticness", 0.0, 1.0, (0.0, 1.0), 0.05,
            help="Acoustic vs electronic sound"
        )
        
        st.markdown("---")
        
        # Track selection for recommendations
        st.markdown("### 🎯 Track Selection")
        track_options = df['track_name'].tolist()
        selected_track_name = st.selectbox(
            "Select a track for recommendations",
            options=[""] + track_options,
            help="Choose a track to see similar recommendations"
        )
        
        selected_track_idx = None
        if selected_track_name:
            matching_tracks = df[df['track_name'] == selected_track_name]
            if not matching_tracks.empty:
                selected_track_idx = matching_tracks.index[0]
    
    # Main content area
    if not selected_genres:
        st.warning("⚠️ Please select at least one genre to begin exploration")
        return
    
    # Create visualization
    fig, filtered_df = create_modern_visualization(df, selected_genres, feature_filters, selected_track_idx)
    
    # Display main plot
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced statistics dashboard
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
    
    # Genre distribution
    st.markdown('<div class="genre-chart">', unsafe_allow_html=True)
    display_genre_distribution(filtered_df)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations section
    if selected_track_idx is not None:
        display_track_recommendations(df, selected_track_idx, knn_model, scaler, feature_cols)
    
    # Spatial clustering section
    display_cluster_playlists(df, clusters)
    
    # Sample tracks section
    st.markdown("### 🎵 Sample Tracks")
    sample_tracks = filtered_df.sample(min(5, len(filtered_df)))
    
    for _, track in sample_tracks.iterrows():
        st.markdown(f"""
        <div class="track-card">
            <div class="track-title">{track['track_name']}</div>
            <div class="track-artist">{track['artist_name']} • {track['genre'].title()}</div>
            <div class="track-features">
                <span class="feature-badge">Energy: {track['energy']:.2f}</span>
                <span class="feature-badge">Danceability: {track['danceability']:.2f}</span>
                <span class="feature-badge">Valence: {track['valence']:.2f}</span>
                <span class="feature-badge">Acousticness: {track['acousticness']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
