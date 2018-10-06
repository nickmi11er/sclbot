# -*- coding: utf-8 -*-
from threading import Lock
from cachetools import LRUCache
import logging
# ================
# add
# get


class Cache():
    def __init__(self, size=10):
        self.data = LRUCache(size)
        self.cache_lock = Lock()

    """
    Get value from cache with key=key
    Retrun data if data exists, otherwise return _default value
    """
    def get(self, key, _default=False):
        result = _default
        try:
            self.cache_lock.acquire()
            result = self.data.get(key, default=_default)
            self.cache_lock.release()
        except Exception as e:
            logging.exception(e.message)
            return _default
        return result

    """
    Insert or update data with key=key
    Return True if successfull, otherwise return False
    """
    def set(self, key, value):
        try:
            self.cache_lock.acquire()
            self.data.update([(key,value)])
            self.cache_lock.release()
            return True
        except Exception as e:
            logging.exception(e.message)
            return False
