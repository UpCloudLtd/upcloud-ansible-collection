import json
import os
import yaml


def collection_version():
    '''Read collection version from MANIFEST.json or galaxy.yml'''
    plugins_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(plugins_dir, '../MANIFEST.json')) as f:
            data = json.load(f)
            return data.get('collection_info', {}).get('version')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    try:
        with open(os.path.join(plugins_dir, '../galaxy.yml')) as f:
            data = yaml.safe_load(f)
            return data.get('version')
    except (FileNotFoundError, yaml.YAMLError):
        pass

    return None
