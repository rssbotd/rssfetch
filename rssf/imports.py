# This file is placed in the Public Domain.


"imports"


import importlib
import importlib.util
import os
import sys


"modules"


def load(path, mname=None):
    if not os.path.exists(path):
        return None
    if mname is None:
        mname = pathtoname(path)
    if mname is None:
        mname = path.split(os.sep)[-1][:-3]
    spec = importlib.util.spec_from_file_location(mname, path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    if not module:
        return None
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)
    return module


def modules(path):
    return sorted([
                   x[:-3] for x in os.listdir(path)
                   if x.endswith(".py") and not x.startswith("__")
                  ])


"utilities"


def pathtoname(path):
    brk = __name__.split(".")[0]
    splitted = path.split(os.sep)
    res = []
    for splt in splitted[::-1]:
        if splt.endswith(".py"):
           splt = splt[:-3]
        res.append(splt)
        if splt == brk:
            break
    return ".".join(res[::-1])


"interface"


def __dir__():
    return (
        'load',
        'modules'
    )
