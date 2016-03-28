import json
import os
import sys

CONFIG = {
    'hammer_versions': [],
}

if hasattr(sys, 'frozen'):
    CONFIG_DIR = os.path.dirname(sys.executable)
else:
    CONFIG_DIR = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

if os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        CONFIG.update(json.load(f))
