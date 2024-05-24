from datetime import datetime, timedelta


class UserCache:
    def __init__(self, expiry_duration=timedelta(hours=10)):
        self.cache = {}
        self.expiry_duration = expiry_duration
        self.top5 = []


    def get(self, username: str):
        now = datetime.utcnow()
        entry = self.cache.get(username)
        if entry and (now - entry['last_updated']) < self.expiry_duration:
            return entry['response']
        return None

    def set(self, username: str, length: int, response: str, last_updated: datetime):
        self.cache[username] = {
            'response': response,
            'last_updated': last_updated
        }
        self.update_top5(username, length)

    def update_top5(self, username, length):
        # Check if user is already in the top 5 or add new entry
        updated = False
        for entry in self.top5:
            if entry['username'] == username:
                entry['length'] = length
                updated = True
                break
        if not updated:
            self.top5.append({'username': username, 'length': length})

        # Keep only the top 5 entries
        self.top5.sort(key=lambda x: x['length'], reverse=True)
        self.top5 = self.top5[:5]
