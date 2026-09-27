import yaml
import os

CONFIG_PATH = "config/config.yaml"

if not os.path.exists(CONFIG_PATH):
    raise FileExistsError


def read_config(key: str):
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)[key]
    except Exception as e:
        raise
