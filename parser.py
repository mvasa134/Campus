import requests
import json

def get_data_from_api():
    """Отримує дані з API"""
    try:
        response = requests.get("http://roz.kpi.ua/api/endpoint")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return None

data = get_data_from_api()
if data:
    print("Received data:", data)
else:
    print("Failed to receive data")