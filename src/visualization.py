import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class MusicExplorerInterface:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        
    def create_interactive_plot(self, filtered_df):
        """Generate responsive scatter visualization with hover capabilities."""
        fig = px.scatter(
            filtered_df, 
            x='x', y='y',
            color='genre',
            hover_data={
                'track_name': True,
                'artist_name': True,
                'energy': ':.2f',
                'danceability': ':.2f',
                'valence': ':.2f',
                'x': False,
                'y': False
            },
            title='Music Explorer Map',
            width=800, height=600
        )
        
        fig.update_traces(
            marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color='white'))
        )
        
        fig.update_layout(
            xaxis_title="Audio Feature Space - Dimension 1",
            yaxis_title="Audio Feature Space - Dimension 2",
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig