# This file is placed in the Public Domain.


"workdir"


import os
import pathlib
import threading


lock = threading.RLock()
j    = os.path.join


class Workdir:

    name = __file__.rsplit(os.sep, maxsplit=2)[-2]
    wdr = ""


def long(name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def moddir():
    return j(Workdir.wdr, "mods")


def pidname(name):
    return j(Workdir.wdr, f"{name}.pid")


def skel():
    pth = pathlib.Path(store())
    pth.mkdir(parents=True, exist_ok=True)
    pth = pathlib.Path(moddir())
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def setwd(pth):
    Workdir.wdr = pth


def store(pth=""):
    return j(Workdir.wdr, "store", pth)


def strip(pth, nmr=2):
    return j(pth.split(os.sep)[-nmr:])


def types():
    return os.listdir(store())


def wdr(pth):
    return j(Workdir.wdr, pth)


def __dir__():
    return (
        'Workdir',
        'long',
        'moddir',
        'pidname',
        'setwd',
        'skel',
        'store',
        'strip',
        'wdr'
    )
