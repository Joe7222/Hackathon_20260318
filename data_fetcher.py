import requests
import pandas as pd

def fetch_sanjose_flights() -> pd.DataFrame:
    # San Jose area roughly bounded by
    lamin, lamax, lomin, lomax = 37.1, 37.5, -122.1, -121.6
    url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
    
    try:
        # Note: OpenSky API anonymous access might have rate limits
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and data.get("states"):
            # Columns based on OpenSky API specification
            columns = [
                "icao24", "callsign", "origin_country", "time_position", 
                "last_contact", "longitude", "latitude", "baro_altitude", 
                "on_ground", "velocity", "true_track", "vertical_rate", 
                "sensors", "geo_altitude", "squawk", "spi", "position_source"
            ]
            df = pd.DataFrame(data["states"], columns=columns)
            
            # Filter rows with missing critical data
            df = df.dropna(subset=['latitude', 'longitude', 'velocity', 'baro_altitude'])
            
            # Clean callsign
            if 'callsign' in df.columns:
                df['callsign'] = df['callsign'].astype(str).str.strip()
                df = df[df['callsign'] != '']
                
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data from OpenSky API: {e}")
        return pd.DataFrame()
def get_real_weather() -> dict:
    url = "https://api.open-meteo.com/v1/forecast?latitude=37.3394&longitude=-121.895&current=wind_speed_10m&hourly=wind_speed_850hPa"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract current surface wind and the first hourly 850hPa wind (proxy for upper level wind)
        current_wind = data.get("current", {}).get("wind_speed_10m", 0)
        hourly_winds = data.get("hourly", {}).get("wind_speed_850hPa", [])
        upper_wind = hourly_winds[0] if hourly_winds else 0
        
        return {
            "surface_wind_kmh": current_wind,
            "upper_wind_kmh": upper_wind
        }
    except Exception as e:
        print(f"Error fetching data from Open-Meteo API: {e}")
        return {"surface_wind_kmh": 0, "upper_wind_kmh": 0}

if __name__ == "__main__":
    # Test execution
    df_test = fetch_sanjose_flights()
    print(f"Found {len(df_test)} flights overhead.")
    if not df_test.empty:
        print(df_test[['callsign', 'baro_altitude', 'velocity']].head())
