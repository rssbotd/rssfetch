# This file is placed in the Public Domain.


"persistence"


import datetime
import json.decoder
import os
import pathlib
import threading


from .object import fqn, update
from .serial import dump, load


lock = threading.RLock()
j    = os.path.join


class Error(Exception):

    pass


class Cache:

    objs = {}

    @staticmethod
    def add(path, obj):
        Cache.objs[path] = obj

    @staticmethod
    def get(path):
        return Cache.objs.get(path, None)

    @staticmethod
    def long(name):
        split = name.split(".")[-1].lower()
        res = name
        for names in Cache.types():
            if split == names.split(".")[-1].lower():
                res = names
                break
        return res
    
    @staticmethod
    def typed(matcher):
        for key in Cache.objs:
            if matcher not in key:
                continue
            yield key

    @staticmethod
    def types():
        return set(Cache.objs.keys())

    @staticmethod
    def update(path, obj):
        if not obj:
            return
        try:
            update(Cache.objs[path], obj)
        except KeyError:
            Cache.add(path, obj)


def getpath(obj):
    return ident(obj)


def ident(obj):
    return j(fqn(obj),*str(datetime.datetime.now()).split())


def __dir__():
    return (
        'Cache',
        'Error',
        'getpath',
        'ident'
    )
