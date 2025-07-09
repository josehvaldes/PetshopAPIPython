import json
import os

def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "appsettings.json")
    with open(config_path, "r") as f:
        return json.load(f)

settings = load_settings()