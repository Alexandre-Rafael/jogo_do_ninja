import json
import os

PROGRESS_FILE = 'progress.json'


class SaveProgress:
    def __init__(self, progress_file='progress.json'):
        self.progress_file = progress_file

    def save_progress(self, level):
        with open(self.progress_file, 'w') as f:
            json.dump({'level': level}, f)

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                return data.get('level', 0)
        else:
            self.save_progress(0)
            return 0
