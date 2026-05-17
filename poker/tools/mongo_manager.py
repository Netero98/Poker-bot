import base64
import io
import json
import logging
import os
import shutil

from PIL import Image

from poker.tools.helper import get_dir
from poker.tools.singleton import Singleton

log = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(_PROJECT_ROOT, 'data')
TABLES_DIR = os.path.join(DATA_DIR, 'tables')


def _name_to_filename(table_name):
    return table_name.replace('/', '_').replace(' ', '_').replace("'", '_')


class MongoManager(metaclass=Singleton):
    """Load table data, strategies and images from local data directory."""

    def __init__(self):
        pass

    def _load_table_json(self, table_name):
        fname = _name_to_filename(table_name) + '.json'
        fpath = os.path.join(TABLES_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(
                f"Table '{table_name}' not found locally. "
                f"Expected file: {fpath}")
        with open(fpath, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        if isinstance(raw, list):
            raw = raw[0]
        return raw

    def _convert_table(self, raw):
        table_converted = {}
        for key, value in raw.items():
            try:
                if isinstance(value, (dict, int, list, float)):
                    table_converted[key] = value
                elif isinstance(value, str) and value[:2] == 'iV':
                    table_converted[key] = base64.b64decode(value)
                else:
                    table_converted[key] = value
            except TypeError:
                pass
        return table_converted

    def get_table(self, table_name):
        raw = self._load_table_json(table_name)
        return self._convert_table(raw)

    def load_table_nn_weights(self, table_name: str):
        log.info("Loading neural network weights for card recognition from local data...")
        fname = _name_to_filename(table_name) + '_weights.h5'
        fpath = os.path.join(TABLES_DIR, fname)
        if not os.path.exists(fpath):
            log.error(f"No neural network weights found for '{table_name}'. "
                      f"Expected: {fpath}")
            return
        dest = os.path.join(get_dir('codebase'), 'loaded_model.h5')
        shutil.copy2(fpath, dest)
        log.info("Loaded weights from %s", fpath)

    def load_table_image(self, image_name, table_name):
        table_dict = self.get_table(table_name)
        if image_name not in table_dict:
            raise KeyError(f"Image '{image_name}' not found in table '{table_name}'")
        raw = table_dict[image_name]
        if isinstance(raw, bytes):
            return Image.open(io.BytesIO(raw))
        raise ValueError(f"Image '{image_name}' is not in binary format")

    def get_available_tables(self, computer_name=None):
        list_path = os.path.join(TABLES_DIR, '_available_tables.json')
        if not os.path.exists(list_path):
            local_tables = []
            for fname in os.listdir(TABLES_DIR):
                if fname.endswith('.json') and not fname.startswith('_'):
                    local_tables.append(fname[:-5])
            return local_tables
        with open(list_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_table_owner(self, table_name):
        raw = self._load_table_json(table_name)
        return raw.get('_owner', '')

    # ── Methods that wrote to the remote server are now local no-ops or save to disk ──

    def save_image(self, table_name, label, image):
        log.warning("save_image: remote upload removed. Saving locally is not implemented.")

    def update_table_image(self, pil_image, label, table_name):
        log.warning("update_table_image: remote upload removed. Saving locally is not implemented.")

    def update_state(self, state, label, table_name):
        log.warning("update_state: remote update removed.")

    def update_tensorflow_model(self, table_name, hdf5_file, model_str, class_mapping):
        log.warning("update_tensorflow_model: remote upload removed.")

    def increment_plays(self, table_name):
        pass

    def get_rounds(self, game_id):
        return []

    def create_new_table(self, table_name):
        log.warning("create_new_table: remote operation removed.")
        return None

    def create_new_table_from_old(self, table_name, old_table_name):
        log.warning("create_new_table_from_old: remote operation removed.")
        return None

    def save_coordinates(self, table_name, label, coordinates_dict):
        log.warning("save_coordinates: remote operation removed.")

    def delete_table(self, table_name, owner):
        log.warning("delete_table: remote operation removed.")

    def get_top_strategies(self):
        import pandas as pd
        return pd.DataFrame()