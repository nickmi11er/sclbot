# -*- coding: utf-8 -*-
import os

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ASSETS_DIR = os.path.join(ROOT_PATH, 'assets')

DB_PATH = ASSETS_DIR + '/data.sqlite'
SCHEMA_PATH = ASSETS_DIR + '/schema.sql'
LOG_PATH = ROOT_PATH + '/log.txt'
SCL_API = os.getenv('SCL_API', 'http://localhost:9000')
BOT_MODE = os.getenv('MODE', 'test')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = os.getenv('PROXY')
if PROXY:
    args = PROXY.split(';')
    REQUEST_KWARGS = {
        'proxy_url':'socks5://' + args[0] + '/',
        'urllib3_proxy_kwargs' : {
            "username" : args[1],
            "password" : args[2]
        }
    }
else:
    REQUEST_KWARGS = None

PERMISSION_ERROR = u'Отказано в доступе'
