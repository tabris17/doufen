# encoding: utf-8
import json
from db import dbo, Setting


def get(name, value_type=str, default=None):
    try:
        setting = Setting.get(Setting.name == name)
        value = setting.value
        if value_type == 'json':
            return json.loads(value)
        else:
            return value_type(value)
    except (Setting.DoesNotExist, ValueError):
        return default


def set(name, value, value_type=str):
    try:
        value_formated = json.dumps(value) if value_type == 'json' else value_type(value)
    except ValueError:
        return False

    Setting.insert(name=name, value=value_formated).on_conflict_replace().execute()
    return True
