# -*- coding: utf-8 -*-
import sys
sys.path.append('..')
import data_manager as dm
from cache_manager import Cache
from model import Model

cache = Cache()

class User(Model):
    
    def __init__(self):
        self.username = ''
        self.tg_user_id = ''
        self.role = 0
        self.group_id = 0
        self.group_name = ''


    @classmethod
    def create(cls, args):
        user = User()
        group_name = dm.get_group_by_id(args['group_id'])['group_name']
        args['group_name'] = group_name
        cls._map(user, args)
        return user


    def save(self):
        if self.__hash__() == self.saved_hash:
            return
        self.saved_hash = self.__hash__()
        dm.add_or_update_user(self.username, self.tg_user_id, self.role, self.group_id)
        cache.set(self.tg_user_id, self)


    @staticmethod
    def _get_from_cache(tg_user_id):
        user = cache.get(tg_user_id)
        if user:
            return user
        else:
            return None


    @staticmethod
    def _fetch_by_id(tg_user_id):
        user = User()
        user_entity = dm.get_user(tg_user_id)
        if user_entity:
            user._map(user_entity)
            cache.set(user.tg_user_id, user)
            return user
        else:
            return None

    @staticmethod
    def _get_all():
        return dm.users_list()
        
            




    