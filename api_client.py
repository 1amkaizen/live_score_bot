import requests
from settings import settings

def fetch_live_scores():
    url = 'http://api.isportsapi.com/sport/football/livescores'
    params = {'api_key': settings.api_key}
    r = requests.get(url, params=params)
    data = r.json()
    return data.get('data', [])
