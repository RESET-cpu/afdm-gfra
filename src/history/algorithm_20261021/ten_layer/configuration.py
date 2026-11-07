"""Inference constants selected before the test panel was evaluated."""
import json
from afdm_jadcedd.project import CONFIGS

CONFIG_PATH = CONFIGS / 'final/receiver.json'
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
