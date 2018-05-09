# encoding: utf-8
import json
from db import dbo, Setting


def get(name, value_type=str):
    try:
        setting = Setting.get(Setting.name == name)
        value = setting.value
        if value_type == 'json':
            return json.loads(value)
        else:
            return value_type(value)
    except (Setting.DoesNotExist, ValueError):
        return
