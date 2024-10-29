import json
from datetime import datetime

def load_current_album(file_path="data/active_album.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_current_album(album_data, file_path="data/active_album.json"):
    with open(file_path, "w") as f:
        json.dump(album_data, f, indent=4)

def set_current_album(album_id, name, artist, file_path="data/active_album.json"):
    current_album = {
        "album_id": album_id,
        "name": name,
        "artist": artist,
        "date_selected": datetime.now().strftime("%Y-%m-%d")
    }
    save_current_album(current_album, file_path)

def get_current_album(file_path="data/active_album.json"):
    """Loads the current album from the JSON file."""
    try:
        with open(file_path, "r") as f:
            album = json.load(f)
            if album and album.get("album_id"):
                return album
            return None
    except FileNotFoundError:
        return None