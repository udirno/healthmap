import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Enhanced page configuration
st.set_page_config(
    page_title="Music Explorer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Apple Music aesthetic
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric > div {
        color: white !important;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    h1 {
        font-weight: 600;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    .stSlider > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_enhanced_data():
    """Load enhanced dataset with authentic metadata."""
    try:
        return pd.read_csv('data/spotify_tracks_enhanced.csv')
    except FileNotFoundError:
        return pd.read_csv('data/spotify_tracks_embedded.csv')

def create_modern_visualization(df, selected_genres, feature_filters):
    """Generate Apple Music-inspired visualization."""
    
    # Apply comprehensive filtering
    filtered_df = df[df['genre'].isin(selected_genres)]
    
    for feature, (min_val, max_val) in feature_filters.items():
        filtered_df = filtered_df[
            filtered_df[feature].between(min_val, max_val)
        ]
    
    # Modern color palette
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
        
        fig.add_trace(go.Scatter(
            x=genre_data['x'],
            y=genre_data['y'],
            mode='markers',
            name=genre.title(),
            marker=dict(
                color=color_map.get(genre, '#8E8E93'),
                size=10,
                opacity=0.8,
                line=dict(width=1, color='white'),
                symbol='circle'
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
    
    # Modern layout styling
    fig.update_layout(
        title={
            'text': f'Music Similarity Space ({len(filtered_df)} tracks)',
            'font': {'size': 24, 'family': 'SF Pro Display, -apple-system'},
            'x': 0.5
        },
        xaxis_title="Feature Dimension 1",
        yaxis_title="Feature Dimension 2",
        font={'family': 'SF Pro Text, -apple-system', 'size': 14},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font={'size': 16}
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    # Grid styling
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    )
    
    return fig, filtered_df

def display_track_recommendations(df, selected_track_idx, n_recommendations=5):
    """Generate similarity-based recommendations."""
    if selected_track_idx is None:
        return
    
    selected_track = df.iloc[selected_track_idx]
    
    # Calculate Euclidean distances in feature space
    feature_cols = ['x', 'y']
    distances = np.sqrt(
        ((df[feature_cols] - selected_track[feature_cols]) ** 2).sum(axis=1)
    )
    
    # Get closest tracks (excluding the selected track)
    similar_indices = distances.nsmallest(n_recommendations + 1).index[1:]
    recommendations = df.iloc[similar_indices]
    
    st.subheader("🎯 Similar Tracks")
    for _, track in recommendations.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{track['track_name']}**")
                st.markdown(f"*{track['artist_name']}* • {track['genre'].title()}")
            with col2:
                similarity = 1 / (1 + distances.iloc[track.name])
                st.metric("Similarity", f"{similarity:.2f}")

def main():
    # Header section
    st.title("🎵 Music Explorer")
    st.markdown("**Discover musical relationships through interactive visualization**")
    
    # Load enhanced dataset
    df = load_enhanced_data()
    
    # Sidebar controls with modern styling
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Genre selection
        selected_genres = st.multiselect(
            "Genres",
            options=sorted(df['genre'].unique()),
            default=sorted(df['genre'].unique()),
            help="Select genres to display"
        )
        
        st.markdown("---")
        
        # Feature filters
        feature_filters = {}
        
        with st.expander("🎚️ Audio Features", expanded=True):
            feature_filters['energy'] = st.slider(
                "Energy", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="Musical energy and intensity"
            )
            
            feature_filters['danceability'] = st.slider(
                "Danceability", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="Rhythmic suitability for dancing"
            )
            
            feature_filters['valence'] = st.slider(
                "Valence", 0.0, 1.0, (0.0, 1.0), 0.05,
                help="Musical positivity and mood"
            )
    
    # Main content area
    if not selected_genres:
        st.warning("Select at least one genre to begin exploration")
        return
    
    # Create visualization
    fig, filtered_df = create_modern_visualization(df, selected_genres, feature_filters)
    
    # Display main plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracks", len(filtered_df))
    
    with col2:
        st.metric("Genres", len(filtered_df['genre'].unique()))
    
    with col3:
        avg_energy = filtered_df['energy'].mean()
        st.metric("Avg Energy", f"{avg_energy:.2f}")
    
    with col4:
        avg_valence = filtered_df['valence'].mean()
        st.metric("Avg Valence", f"{avg_valence:.2f}")
    
    # Genre distribution
    st.subheader("📊 Genre Distribution")
    genre_counts = filtered_df['genre'].value_counts()
    st.bar_chart(genre_counts)
    
    # Sample tracks
    st.subheader("🎵 Sample Tracks")
    sample_tracks = filtered_df.sample(min(5, len(filtered_df)))
    
    for _, track in sample_tracks.iterrows():
        with st.expander(f"{track['track_name']} • {track['artist_name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Genre:** {track['genre'].title()}")
                st.markdown(f"**Artist:** {track['artist_name']}")
            with col2:
                st.markdown(f"**Energy:** {track['energy']:.2f}")
                st.markdown(f"**Danceability:** {track['danceability']:.2f}")
                st.markdown(f"**Valence:** {track['valence']:.2f}")

if __name__ == "__main__":
    main()