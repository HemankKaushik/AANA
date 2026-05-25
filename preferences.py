import json
import os

PREFS_FILE = "user_preferences.json"

def save_preferences(email, keywords, domain, frequency, summary_type):
    prefs = {
        "email": email,
        "keywords": keywords,
        "domain": domain,
        "frequency": frequency,
        "summary_type": summary_type
    }
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2)
    return True

def load_preferences():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r") as f:
            return json.load(f)
    return None