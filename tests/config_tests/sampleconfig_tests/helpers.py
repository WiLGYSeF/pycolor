import os

from src.pycolor.config import SAMPLE_CONFIG_DIR

def get_sample_config_filename(config_name: str) -> str:
    return os.path.join(SAMPLE_CONFIG_DIR, config_name + '.json')
