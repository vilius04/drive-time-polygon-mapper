"""
Interactive Isochrone Fetcher
Prompts user for address and time range, then fetches isochrone from OpenRouteService API.
"""
import json
import requests
import sys
from typing import Tuple

def geocode_address(address: str) -> Tuple[float, float]:
    """
    Geocode address using Nominatim (OpenStreetMap).
    Returns (longitude, latitude) tuple.
    """
    print(f"Geocoding address: {address}")
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "IsochroneGenerator/1.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    results = response.json()
    if not results:
        raise ValueError(f"Could not geocode address: {address}")
    
    lon = float(results[0]["lon"])
    lat = float(results[0]["lat"])
    print(f"✓ Geocoded to: {lat}, {lon}")
    return lon, lat

def fetch_isochrone(lon: float, lat: float, time_minutes: int, api_key: str) -> dict:
    """
    Fetch isochrone from OpenRouteService API.
    
    Args:
        lon: Longitude
        lat: Latitude
        time_minutes: Time range in minutes
        api_key: ORS API key
    
    Returns:
        GeoJSON FeatureCollection
    """
    print(f"Fetching {time_minutes}-minute isochrone from OpenRouteService...")
    url = "https://api.openrouteservice.org/v2/isochrones/driving-car"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "locations": [[lon, lat]],
        "range": [time_minutes * 60],  # Convert to seconds
        "attributes": ["area", "reachfactor"],
        "range_type": "time"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

def main():
    """Main execution function with interactive prompts."""
    print("=" * 60)
    print("ISOCHRONE GENERATOR - Step 1: Fetch Isochrone Data")
    print("=" * 60)
    print()
    
    # Prompt for API key
    api_key = input("Enter your OpenRouteService API key: ").strip()
    if not api_key:
        print("ERROR: API key is required.")
        print("Get a free key at: https://openrouteservice.org/dev/#/signup")
        sys.exit(1)
    
    # Prompt for address
    print()
    print("Enter the address to calculate from:")
    print("Example: 123 Main St, Chicago, IL 60601")
    address = input("> ").strip()
    if not address:
        print("ERROR: Address is required.")
        sys.exit(1)
    
    # Prompt for time range
    print()
    while True:
        time_input = input("Enter time range in minutes (e.g., 30, 45, 60): ").strip()
        try:
            time_minutes = int(time_input)
            if time_minutes <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    print()
    print("-" * 60)
    
    try:
        # Geocode the address
        lon, lat = geocode_address(address)
        
        # Fetch isochrone
        isochrone = fetch_isochrone(lon, lat, time_minutes, api_key)
        
        # Save to file
        output_file = "isochrone.geojson"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(isochrone, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 60)
        print(f"✓ SUCCESS! Isochrone saved to: {output_file}")
        print(f"Features: {len(isochrone.get('features', []))}")
        print()
        print("Next step: Run process_isochrone.py to remove excluded areas")
        print("=" * 60)
        
    except requests.RequestException as e:
        print(f"\n✗ API Error: {e}")
        if "401" in str(e):
            print("Check that your API key is correct.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
