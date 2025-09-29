
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from typing import List, Dict

class SpotifyDataCollector:
    def __init__(self, client_id: str, client_secret: str):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        self.feature_columns = [
            'danceability', 'energy', 'speechiness', 'acousticness',
            'instrumentalness', 'liveness', 'valence', 'tempo', 'loudness'
        ]
    
    def search_tracks_by_query(self, query: str, limit: int = 50) -> List[Dict]:
        tracks_data = []
        try:
            limit = min(limit, 50)
            results = self.sp.search(q=query, type='track', limit=limit, market='US')
            
            track_ids = []
            track_metadata = {}
            
            for track in results['tracks']['items']:
                if track['id']:  # Only require track ID
                    track_id = track['id']
                    track_ids.append(track_id)
                    track_metadata[track_id] = {
                        'track_name': track['name'],
                        'artist_name': track['artists'][0]['name'],
                        'album_name': track['album']['name'],
                        'popularity': track['popularity'],
                        'preview_url': track.get('preview_url', ''),
                        'duration_ms': track['duration_ms']
                    }
            
            if track_ids:
                audio_features = self.sp.audio_features(track_ids)
                for features in audio_features:
                    if features and features['id'] in track_metadata:
                        track_data = {
                            'track_id': features['id'],
                            **track_metadata[features['id']],
                            **{col: features[col] for col in self.feature_columns}
                        }
                        tracks_data.append(track_data)
                        
        except Exception as e:
            print(f"Error: {e}")
        
        return tracks_data
    
    def collect_comprehensive_dataset(self, target_size: int = 800) -> pd.DataFrame:
        queries = [
            'Taylor Swift', 'Drake', 'The Beatles', 'Led Zeppelin',
            'Daft Punk', 'Miles Davis', 'Bach', 'Johnny Cash',
            'Radiohead', 'Beyonce', 'Kendrick Lamar', 'Pink Floyd'
        ]
        
        tracks_per_query = min(50, target_size // len(queries))
        all_tracks = []
        
        for query in queries:
            print(f"Processing: {query}")
            query_tracks = self.search_tracks_by_query(query, tracks_per_query)
            all_tracks.extend(query_tracks)
            print(f"  Acquired: {len(query_tracks)} tracks")
            time.sleep(0.1)
        
        if not all_tracks:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_tracks)
        df = df.drop_duplicates(subset='track_id')
        
        print(f"\nFinal dataset: {len(df)} tracks")
        print(f"Preview coverage: {(df['preview_url'] != '').sum()}/{len(df)}")
        
        return df
