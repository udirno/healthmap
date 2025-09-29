import numpy as np
import pandas as pd
import random

class AuthenticMusicGenerator:
    def __init__(self):
        self.genre_vocabularies = {
            'electronic': {
                'track_templates': [
                    'Synthetic {noun}', 'Digital {noun}', 'Neon {noun}', 
                    '{adjective} Circuit', 'Binary {noun}', 'Pulse {adjective}',
                    '{noun} Matrix', 'Algorithm {adjective}', 'Data {noun}'
                ],
                'adjectives': ['Dreams', 'Waves', 'Signals', 'Frequency', 'Flow', 'Current'],
                'nouns': ['Synthesis', 'Amplitude', 'Resonance', 'Phase', 'Filter', 'Delay'],
                'artists': [
                    'Neural Collective', 'Voltage Drop', 'Data Stream', 'Bit Shift', 
                    'Analog Soul', 'Digital Phantom', 'Circuit Theory', 'Binary Echo'
                ]
            },
            'classical': {
                'track_templates': [
                    '{adjective} in {key}', 'Sonata {adjective}', '{noun} No. {number}',
                    'Prelude {adjective}', 'Etude in {key}', '{adjective} {noun}',
                    'Variations on {adjective}', 'Concerto {adjective}'
                ],
                'adjectives': ['Melancholic', 'Triumphant', 'Serene', 'Passionate', 'Contemplative'],
                'nouns': ['Symphony', 'Fugue', 'Adagio', 'Allegro', 'Andante', 'Nocturne'],
                'keys': ['C Major', 'D Minor', 'F Sharp', 'B Flat', 'E Minor', 'A Major'],
                'artists': [
                    'Chamber Orchestra', 'Piano Virtuoso', 'String Ensemble', 'Baroque Collective',
                    'Symphony Orchestra', 'Classical Quartet', 'Soloist Academy', 'Concert Series'
                ]
            },
            'rock': {
                'track_templates': [
                    '{adjective} {noun}', 'Thunder {noun}', 'Steel {adjective}',
                    'Fire {noun}', 'Electric {adjective}', 'Wild {noun}',
                    '{noun} Revolution', 'Highway {adjective}', 'Iron {noun}'
                ],
                'adjectives': ['Storm', 'Thunder', 'Lightning', 'Fire', 'Steel', 'Iron'],
                'nouns': ['Highway', 'Revolution', 'Machine', 'Freedom', 'Rebellion', 'Spirit'],
                'artists': [
                    'Iron Thunder', 'Electric Storm', 'Steel Highway', 'Fire Machine',
                    'Wild Thunder', 'Lightning Steel', 'Iron Revolution', 'Storm Highway'
                ]
            },
            'jazz': {
                'track_templates': [
                    '{adjective} {noun}', 'Blue {noun}', 'Midnight {adjective}',
                    'Smooth {noun}', '{adjective} Sessions', 'Late Night {noun}',
                    '{noun} Improvisations', 'After Hours {adjective}'
                ],
                'adjectives': ['Blue', 'Smooth', 'Cool', 'Hot', 'Sweet', 'Mellow'],
                'nouns': ['Sessions', 'Groove', 'Swing', 'Bebop', 'Blues', 'Standard'],
                'artists': [
                    'Blue Note Collective', 'Smooth Jazz Ensemble', 'Cool Cat Trio',
                    'Hot Jazz Quartet', 'Midnight Sessions', 'Urban Jazz Society'
                ]
            },
            'pop': {
                'track_templates': [
                    '{adjective} {noun}', 'Summer {adjective}', 'Dancing {noun}',
                    'Golden {noun}', 'Perfect {adjective}', 'Shining {noun}',
                    'Beautiful {adjective}', 'Forever {noun}'
                ],
                'adjectives': ['Dreams', 'Lights', 'Hearts', 'Nights', 'Days', 'Love'],
                'nouns': ['Summer', 'Dancing', 'Golden', 'Perfect', 'Shining', 'Beautiful'],
                'artists': [
                    'Pop Collective', 'Summer Vibes', 'Golden Hour', 'Perfect Harmony',
                    'Shining Stars', 'Beautiful Dreams', 'Forever Young', 'Dancing Light'
                ]
            }
        }
    
    def generate_track_name(self, genre):
        """Generate semantically coherent track titles."""
        vocab = self.genre_vocabularies[genre]
        template = random.choice(vocab['track_templates'])
        
        result = template
        if '{adjective}' in template:
            result = result.replace('{adjective}', random.choice(vocab['adjectives']))
        if '{noun}' in template:
            result = result.replace('{noun}', random.choice(vocab['nouns']))
        if '{key}' in template and genre == 'classical':
            result = result.replace('{key}', random.choice(vocab['keys']))
        if '{number}' in template:
            result = result.replace('{number}', str(random.randint(1, 99)))
            
        return result
    
    def generate_artist_name(self, genre):
        """Generate realistic artist nomenclature."""
        return random.choice(self.genre_vocabularies[genre]['artists'])
    
    def enhance_dataset_authenticity(self, df):
        """Replace synthetic metadata with realistic alternatives."""
        np.random.seed(42)
        random.seed(42)
        
        enhanced_data = []
        
        for _, row in df.iterrows():
            genre = row['genre']
            enhanced_row = row.copy()
            
            # Generate authentic metadata
            enhanced_row['track_name'] = self.generate_track_name(genre)
            enhanced_row['artist_name'] = self.generate_artist_name(genre)
            
            # Create unique track ID
            enhanced_row['track_id'] = f"{genre}_{hash(enhanced_row['track_name']) % 10000:04d}"
            
            enhanced_data.append(enhanced_row)
        
        return pd.DataFrame(enhanced_data)

# Execution protocol
generator = AuthenticMusicGenerator()
df_original = pd.read_csv('data/spotify_tracks_embedded.csv')
df_enhanced = generator.enhance_dataset_authenticity(df_original)

# Validation
print("Enhanced Track Examples:")
for genre in df_enhanced['genre'].unique():
    sample = df_enhanced[df_enhanced['genre'] == genre].sample(2)
    for _, track in sample.iterrows():
        print(f"• {track['track_name']} by {track['artist_name']} [{genre}]")

# Persistence
df_enhanced.to_csv('data/spotify_tracks_enhanced.csv', index=False)
print(f"\nEnhanced dataset saved: {len(df_enhanced)} tracks with authentic metadata")