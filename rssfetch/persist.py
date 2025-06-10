# This file is placed in the Public Domain.


"persistence"


import datetime
import json.decoder
import os
import pathlib
import threading


from .cache  import Cache
from .object import fqn, update
from .serial import dump, load


lock = threading.RLock()
j    = os.path.join


class Error(Exception):

    pass


class Workdir:

    name = __file__.rsplit(os.sep, maxsplit=2)[-2]
    wdr = ""


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def getpath(obj):
    return j(store(ident(obj)))


def ident(obj):
    return j(fqn(obj),*str(datetime.datetime.now()).split())


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                raise Error(path) from ex
        Cache.update(path, obj)


def setwd(pth):
    Workdir.wdr = pth


def skel():
    pth = pathlib.Path(store())
    pth.mkdir(parents=True, exist_ok=True)
    pth = pathlib.Path(moddir())
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def store(pth=""):
    return j(Workdir.wdr, "store", pth)


def strip(pth, nmr=2):
    return j(pth.split(os.sep)[-nmr:])


def write(obj, path=""):
    with lock:
        if path == "":
            path = getpath(obj)
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


def __dir__():
    return (
        'Error',
        'Workdir',
        'cdir',
        'getpath',
        'ident',
        'read',
        'setwd',
        'store',
        'strip',
        'write'
    )
