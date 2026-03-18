import requests
import pandas as pd
import json

# Local nemotron endpoint according to dgx-spark-playbooks
NEMOTRON_API_URL = "http://localhost:30000/v1/chat/completions"
MODEL_NAME = "nemotron"

def generate_eco_proposal(flight_row: pd.Series, weather_data: dict) -> str:
    callsign = flight_row.get("callsign", "Unknown")
    altitude = flight_row.get("baro_altitude", 0)
    velocity = flight_row.get("velocity", 0)
    upper_wind = weather_data.get("upper_wind_kmh", 0)
    
    prompt = f"""
You are an AI assistant specialized in aviation aerodynamics and environmental impact reduction. Please analyze the following real-time parameters from an aircraft.
Based on physical principles (such as combining the trade-offs of altitude vs. air density drag and headwinds/tailwinds), autonomously infer whether the aircraft should maintain or change its current altitude.
Provide the optimal actionable recommendation for the pilot to minimize CO2 emissions and fuel consumption, along with a concise technical physical justification.

**CRITICAL INSTRUCTION**: You must provide your ENTIRE response in TWO languages. 
First, output the complete response in English.
Then, output the exact same response translated into Japanese.
Format your response clearly with headers for "English" and "日本語".

Flight: {callsign}
Altitude: {altitude} meters
Velocity: {velocity} m/s
Upper Wind Speed (850hPa proxy): {upper_wind} km/h
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system", 
                "content": "You are a professional aviation software assistant. You ALWAYS output your responses in both English and Japanese (Bilingual)."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 800
    }
    
    try:
        response = requests.post(NEMOTRON_API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
        response.raise_for_status()
        result = response.json()
        
        # Check standard OpenAI API response format
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            return message.get("content", "No proposal found in the response.").strip()
            
        return "Unexpected LLM response format."
    except requests.exceptions.ConnectionError:
        return "Connection Error: Please ensure the llama.cpp server is running on localhost:30000 as per the DGX Playbook."
    except Exception as e:
        return f"Error querying local Nemotron LLM: {str(e)}"
