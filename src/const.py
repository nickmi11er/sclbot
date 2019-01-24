# -*- coding: utf-8 -*-
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
assets_dir = os.path.join(root_path, 'assets')

_db_name = assets_dir + '/data.sqlite'
_bot_mode = os.getenv('MODE', 'test')
_bot_token = os.getenv('BOT_TOKEN')
permission_error = u'Отказано в доступе'
