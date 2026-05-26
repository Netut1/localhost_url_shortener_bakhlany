import json
import os
from datetime import datetime

class URLDatabase:
    def __init__(self, db_file='url_database.json', max_records=100):
        self.db_file = db_file
        self.max_records = max_records
        self.load_database()

    def load_database(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.urls = data.get('urls', {})
                self.metadata = data.get('metadata', {})
        else:
            self.urls = {}
            self.metadata = {
                'created': datetime.now().isoformat(),
                'total_urls': 0
            }

    def save_database(self):
        data = {
            'urls': self.urls,
            'metadata': self.metadata
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_url(self, long_url, short_url):
        if len(self.urls) >= self.max_records:
            oldest_key = min(self.urls.keys(), key=lambda k: self.urls[k].get('created_at', ''))
            del self.urls[oldest_key]
        if short_url in self.urls:
            return False, "Короткий URL уже существует"
        for s, data in self.urls.items():
            if data['long_url'] == long_url:
                return True, s
        self.urls[short_url] = {
            'long_url': long_url,
            'created_at': datetime.now().isoformat(),
            'clicks': 0
        }
        self.metadata['total_urls'] = len(self.urls)
        self.save_database()
        return True, short_url

    def get_long_url(self, short_url):
        if short_url in self.urls:
            self.urls[short_url]['clicks'] += 1
            self.save_database()
            return self.urls[short_url]['long_url']
        return None

    def get_short_url(self, long_url):
        for short_url, data in self.urls.items():
            if data['long_url'] == long_url:
                return short_url
        return None

    def clear_database(self):
        self.urls = {}
        self.metadata = {
            'created': datetime.now().isoformat(),
            'total_urls': 0
        }
        self.save_database()
        return True, "База данных очищена"

    def get_stats(self):
        return {
            'total_urls': len(self.urls),
            'max_records': self.max_records,
            'database_file': self.db_file
        }