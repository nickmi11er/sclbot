# -*- coding: utf-8 -*-
import operator

class Model(object):
    saved_hash = 0

    # Describe all attributes of class
    # Note that the names of attributes MUST be the same as the names in DB
    def __init__(self):
        pass
        

    #Interface
    #=========================================

    # Create new entity with attributes 
    # in args {name:value} by using reflection
    @classmethod
    def create(cls, args):
        raise NotImplementedError('Method not implemented')

    # Get entity from cache or DB by key
    @classmethod
    def get(cls, key):
        entity = cls._get_from_cache(key)
        if entity:
            return entity
        entity = cls._fetch_by_id(key)
        if entity:
            return entity
        return entity

    @classmethod
    def getAll(cls):
        res_objs = []
        entities =  cls._get_all()
        for ent in entities:
            res_objs.append(cls.create(ent))
        return res_objs

    # Add or update entity in DB and/or cache
    def save(self):
        raise NotImplementedError('Method not implemented')

    #=========================================


    @staticmethod
    def _get_from_cache(key):
        raise NotImplementedError('Method not implemented')

    @staticmethod
    def _fetch_by_id(key):
        raise NotImplementedError('Method not implemented')

    @staticmethod
    def _get_all():
        raise NotImplementedError('Method not implemented')
        

    # Return hash summ of all self attributes with their values
    # except saved_hash
    def __hash__(self):
        args = vars(self)
        _key = ()
        for k in sorted(args, key=args.get):
            if k == 'saved_hash':
                continue
            _key = _key + (args[k],)
        return hash(_key)


    def __str__(self):
        res = ''
        args = vars(self)
        for k in sorted(args, key=args.get):
            val = args[k]
            if isinstance(val, basestring):
                val = val.encode('utf-8')
            else:
                val = str(val)
            res = res + k + ': ' + val + '\n'
        return res


    # Map args values on object attributes by using reflection
    # It is better way to describe all attributes in __init__
    # to avoid to access nonexistent attributes in runtime
    def _map(self, args):
        for key in args:
            self.__add_attr(key, args[key])

    def __add_attr(self, name, value):
        setattr(self, name, value)