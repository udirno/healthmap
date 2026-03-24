"""
Ingest climate data from OpenWeather API
"""
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_weather_data(city, country_code):
    """Fetch current weather data for a city"""

    if not OPENWEATHER_API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country_code}",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        weather_data = {
            "city": city,
            "country": country_code,
            "date": datetime.now().date(),
            "temp_avg": data['main']['temp'],
            "temp_min": data['main']['temp_min'],
            "temp_max": data['main']['temp_max'],
            "humidity": data['main']['humidity'],
            "pressure": data['main']['pressure'],
            "wind_speed": data['wind']['speed']
        }

        return weather_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {city}: {e}")
        return None

def main():
    print("Starting climate data ingestion...")

    # Major cities to track
    cities = [
        ("New York", "US"),
        ("London", "GB"),
        ("Tokyo", "JP"),
        ("Mumbai", "IN"),
        ("Sao Paulo", "BR"),
        ("Lagos", "NG"),
        ("Sydney", "AU")
    ]

    results = []
    for city, country in cities:
        print(f"Fetching weather for {city}, {country}...")
        data = fetch_weather_data(city, country)
        if data:
            results.append(data)
            print(f"  Temperature: {data['temp_avg']}°C, Humidity: {data['humidity']}%")

    print(f"\nFetched weather data for {len(results)} cities")
    print("Climate ingestion complete!")

if __name__ == "__main__":
    main()
