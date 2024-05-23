from datetime import datetime, timedelta


class UserCache:
    def __init__(self, expiry_duration=timedelta(hours=10)):
        self.cache = {}
        self.expiry_duration = expiry_duration

    def get(self, username: str):
        now = datetime.utcnow()
        entry = self.cache.get(username)
        if entry and (now - entry['last_updated']) < self.expiry_duration:
            return entry['response']
        return None

    def set(self, username: str, response: str, last_updated: datetime):
        self.cache[username] = {
            'response': response,
            'last_updated': last_updated
        }
