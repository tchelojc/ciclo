import requests
from datetime import datetime
from .cache import cache  # Implemente um sistema simples de cache
import json
from pathlib import Path

class HistoricalEventsAPI:
    def __init__(self):
        self.base_url = "https://api.example.com/events"  # Substitua por uma API real
        self.cache_timeout = 86400  # 24 horas em segundos

    def get_events(self, start_year, end_year):
        """Obtém eventos históricos de uma API ou arquivo local"""
        try:
            return self._get_online_events(start_year, end_year)
        except requests.exceptions.RequestException:
            return self._get_local_events()

    def _get_online_events(self, start_year, end_year):
        """Busca eventos de uma API (implementação de exemplo)"""
        params = {
            "start_date": f"{start_year}-01-01",
            "end_date": f"{end_year}-12-31",
            "limit": 50
        }
        response = requests.get(self.base_url, params=params, timeout=5)
        response.raise_for_status()
        return self._parse_events(response.json())

    def _get_local_events(self):
        """Carrega eventos de um arquivo JSON local"""
        path = Path(__file__).parent.parent / "data/historical_events.json"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_events(self, api_data):
        """Corrigido para garantir estrutura correta"""
        parsed = []
        for e in api_data.get('results', []):
            try:
                parsed.append({
                    "year": int(datetime.strptime(e['date'], "%Y-%m-%d").year),
                    "title": str(e['title']),
                    "description": str(e.get('description', '')),
                    "type": "historical"
                })
            except (KeyError, ValueError):
                continue
        return parsed

    def _load_backup_events(self):
        """Carrega eventos locais se a API falhar"""
        import json
        with open('data/backup_events.json') as f:
            return json.load(f)