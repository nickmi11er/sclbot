# -*- coding: utf-8 -*-
import const


class Store():
    def __init__(self, storename=None):
        self.dct = dict()
        self.storename = 'default.dat' if storename is None else storename 

    def get(self, key):
        if key in self.dct:
            return self.dct[key]
        else:
            return None

    #Сохраняет значение в памяти
    #Запрещено перезаписывать значения, только добавлять
    def mset(self, key, value):
        if key in self.dct:
            return False
        else:
            self.dct[key] = value
            return True
    
    #Сохраняет добавленные элементы в файл-хранилище
    #def save(self):
    #    with open(const.store_dir+'/'+self.storename, 'w') as f:
    #        for key, val in self.dct.iteritems():
    #            f.write('{0}={1}'.format(key, val))

class SettingStore(Store):
    def __init__(self, storename=None):
        self.dct = dict()
        self.storename = 'settings.dat' if storename is None else storename
        with open(const.assets_dir+'/'+self.storename, 'r') as f:
            ln = f.readline().rstrip()
            l = [x.strip() for x in ln.split('=')]
            self.dct[l[0]] = l[1]
    

    
