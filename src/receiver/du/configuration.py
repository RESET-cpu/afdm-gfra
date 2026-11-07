"""Inference constants selected before the test panel was evaluated."""
import json
from workspace import CONFIGS

CONFIG_PATH = CONFIGS / 'final/receiver.json'
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
