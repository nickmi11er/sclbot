# -*- coding: utf-8 -*-
import os.path

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
assets_dir = os.path.join(root_path, 'assets')

_db_name = assets_dir + '/data.sqlite'

permission_error = u'Отказано в доступе'
