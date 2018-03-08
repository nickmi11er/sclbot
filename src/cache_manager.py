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


# cs = Cache()


# #testing

# _ns = 4
# pool = list()

# _u = [{x:str(x)} for x in range(0, 100)]
# users = {}
# for k, v in enumerate(_u):
#     users[k] = v[k]
# print users


# def find_user(cache, id=-1, _defalut=False):
#     if id == -1:
#         return _defalut
#     else:
#         user = cache.get(id)
#         return user

# def add_user(cache, id=-1, val=False):
#     if id == -1:
#         return False
#     else:
#         u = cache.set(id, val)
#         if not u:
#             print 'Cannot insert user %d' % id
#             return False
#         return True

# def use_cache(cache):
#     while True:
#         _num = randint(0, 99)
#         try:
#             print 'Try to find user %d' % _num
#             user = find_user(cache, _num, False)
#             if not user:
#                 global users
#                 print 'User(%d) not found' % _num
#                 add_user(cache, _num, users[_num])
#             else:
#                 print 'User(%d) found in thread %s' % (_num, current_thread().getName())
#         except Exception as e:
#                 print 'Exception %s' % e.message
#                 sys.exit(0)



# pool = list()
# for x in range(0, 4):
#     _t = Thread(target=use_cache, args=(cs,))
#     _t.start()
#     pool.append(_t)

# for _t in pool:
#     _t.join()
