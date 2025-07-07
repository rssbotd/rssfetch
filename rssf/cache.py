# This file is placed in the Public Domain.


"cache"


import datetime
import os
import threading
import time


from .object import fqn, items, update


class Cache:

    objs = {}

    @staticmethod
    def add(path, obj):
        Cache.objs[path] = obj

    @staticmethod
    def get(path):
        return Cache.objs.get(path, None)


    @staticmethod
    def update(path, obj):
        if not obj:
            return
        try:
            update(Cache.objs[path], obj)
        except KeyError:
            Cache.add(path, obj)


def find(clz, selector=None, deleted=False, matching=False):
    clz = long(clz)
    if selector is None:
        selector = {}
    for pth in typed(clz):
        obj = Cache.get(pth)
        if not deleted and isdeleted(obj):
            continue
        if selector and not search(obj, selector, matching):
            continue
        yield pth, obj


def fntime(daystr):
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    datestr = datestr.replace("_", " ")
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    timed = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        timed += float('.' + rest)
    return float(timed)


def getpath(obj):
    return ident(obj)


def ident(obj):
    return os.path.join(fqn(obj),*str(datetime.datetime.now()).split())


def isdeleted(obj):
    return '__deleted__' in dir(obj) and obj.__deleted__


def long(name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res
    

def typed(matcher):
    for key in Cache.objs:
        if matcher not in key:
            continue
        yield key


def types():
    return set(Cache.objs.keys())


def search(obj, selector, matching=False):
    res = False
    if not selector:
        return res
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower() or value == "match":
            res = True
        else:
            res = False
            break
    return res


def __dir__():
    return (
        'Cache',
        'find',
        'fns',
        'fntime',
        'getpath',
        'ident'
        'last',
        'search'
    )
