import json
import os

DEFAULTS = {
    "music_volume": 0.2,
    "sfx_volume": 0.2,
    "master_volume": 1.0
}


def _config_path():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'config.json')


def load_config():
    path = _config_path()
    if not os.path.isfile(path):
        return DEFAULTS.copy()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            out = DEFAULTS.copy()
            out.update({k: data.get(k, v) for k, v in DEFAULTS.items()})
            return out
    except Exception:
        return DEFAULTS.copy()


def save_config(cfg: dict):
    path = _config_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception:
        return False
