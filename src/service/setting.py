# encoding: utf-8
import json
from db import dbo, Setting


DEFAULT_SERVICE_PORT = 8398
DEFAULT_SERVICE_HOST = '127.0.0.1'
DEFAULT_DATEBASE = 'var/data/graveyard.db'
DEFAULT_CACHE_PATH = 'var/cache'
DEFAULT_DEBUG_MODE = False

settings = {
    'debug': DEFAULT_DEBUG_MODE,
    'cache': DEFAULT_CACHE_PATH,
    'database': DEFAULT_DATEBASE,
    'port': DEFAULT_SERVICE_PORT,
}

def get(name, value_type=str, default=None):
    try:
        setting = Setting.get(Setting.name == name)
        value = setting.value
        if value_type == 'json':
            return json.loads(value)
        elif value_type is bool:
            return bool(int(value))
        else:
            return value_type(value)
    except (Setting.DoesNotExist, ValueError):
        return default


def set(name, value, value_type=str):
    try:
        if value_type == 'json':
            value_formated = json.dumps(value)
        elif value_type is bool:
            value_formated = 1 if value else 0
        else:
            value_formated = value_type(value)
    except ValueError:
        return False

    Setting.insert(name=name, value=value_formated).on_conflict_replace().execute()
    return True
