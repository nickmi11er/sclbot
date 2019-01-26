# -*- coding: utf-8 -*-
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
assets_dir = os.path.join(root_path, 'assets')

DB_PATH = assets_dir + '/data.sqlite'
SCHEMA_PATH = assets_dir + '/schema.sql'
LOG_PATH = root_path + '/log.txt'
SCL_API = os.getenv('SCL_API', 'http://localhost:9000')
BOT_MODE = os.getenv('MODE', 'test')
BOT_TOKEN = os.getenv('BOT_TOKEN')
_proxy = os.getenv('PROXY')
if _proxy:
    args = _proxy.split(';')
    REQUEST_KWARGS={
        'proxy_url': 'socks5://' + args[0] + '/', 
        'urllib3_proxy_kwargs': {
            "username": args[1], 
            "password": args[2]
        }
    }
else:
    REQUEST_KWARGS = None

permission_error = u'Отказано в доступе'
