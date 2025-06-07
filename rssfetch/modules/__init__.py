# This file is placed in the Public Domain.


"modules"


import hashlib
import importlib
import importlib.util
import inspect
import logging
import os
import sys
import threading
import time
import _thread


from ..fleet  import Fleet
from ..object import Object, items, keys
from ..thread import later, launch


STARTTIME = time.time()


lock = threading.RLock()
path = os.path.dirname(__file__)


CHECKSUM = "d153722979abc40b8731588035425777"
MD5      = {}
NAMES    = {}


class Default(Object):

    def __getattr__(self, key):
        if key not in self:
            setattr(self, key, "")
        return self.__dict__.get(key, "")


class Main(Default):

    debug   = False
    gets    = Default()
    ignore  = "now,req"
    init    = ""
    level   = "warn"
    md5     = True
    name    = __name__.split(".", maxsplit=1)[0]
    opts    = Default()
    otxt    = ""
    sets    = Default()
    verbose = False
    version = 323


"runtime"


def inits(names):
    modz = []
    for name in sorted(spl(names)):
        try:
            mod = load(name)
            if not mod:
                continue
            if "init" in dir(mod):
                thr = launch(mod.init)
                modz.append((mod, thr))
        except Exception as ex:
            later(ex)
            _thread.interrupt_main()
    return modz


def parse(obj, txt=""):
    if txt == "":
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args   = []
    obj.cmd    = ""
    obj.gets   = Default()
    obj.index  = None
    obj.mod    = ""
    obj.opts   = ""
    obj.result = {}
    obj.sets   = Default()
    obj.silent = Default()
    obj.txt    = txt
    obj.otxt   = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            setattr(obj.silent, key, value)
            setattr(obj.gets, key, value)
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


"modules"


def check(name, md5=""):
    if not CHECKSUM:
        return True
    mname = f"{__name__}.{name}"
    if sys.modules.get(mname):
        return True
    pth = os.path.join(path, name + ".py")
    spec = importlib.util.spec_from_file_location(mname, pth)
    if not spec:
        return False
    if md5sum(pth) == (md5 or MD5.get(name, "")):
        return True
    if CHECKSUM and Main.md5:
        debug(f"{name} failed md5sum check")
    return False


def getmod(name):
    mname = f"{__name__}.{name}"
    mod = sys.modules.get(mname, None)
    if mod:
        return mod
    pth = os.path.join(path, name + ".py")
    spec = importlib.util.spec_from_file_location(mname, pth)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    if mod:
        spec.loader.exec_module(mod)
        sys.modules[mname] = mod
    return mod


def gettbl(name):
    pth = os.path.join(path, "tbl.py")
    if not os.path.exists(pth):
        debug("tbl.py is not there")
        return {}
    if CHECKSUM and (md5sum(pth) != CHECKSUM):
        debug("table checksum doesn't match")
        return {}
    try:
        mod = getmod("tbl")
    except FileNotFoundError:
        debug("tbl module not found")
        return None
    return getattr(mod, name, {})


def load(name):
    with lock:
        if name in Main.ignore:
            return None
        module = None
        mname = f"{__name__}.{name}"
        module = sys.modules.get(mname, None)
        if not module:
            pth = os.path.join(path, f"{name}.py")
            if not os.path.exists(pth):
                return None
            spec = importlib.util.spec_from_file_location(mname, pth)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            if not module:
                return None
            spec.loader.exec_module(module)
            sys.modules[mname] = module
        setdebug(module)
        return module


def md5sum(modpath):
    with open(modpath, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return str(hashlib.md5(txt).hexdigest())


def mods(names=""):
    res = []
    for nme in modules():
        if names and nme not in spl(names):
            continue
        mod = load(nme)
        if not mod:
            continue
        res.append(mod)
    return res


def modules(mdir=""):
    return sorted([
                   x[:-3] for x in os.listdir(mdir or path)
                   if x.endswith(".py") and not x.startswith("__") and
                   x[:-3] not in Main.ignore
                  ])


def setdebug(module):
    if Main.debug:
        module.DEBUG = True


def table():
    md5s = gettbl("MD5")
    if md5s:
        MD5.update(md5s)
    names = gettbl("NAMES")
    if names:
        NAMES.update(names)
    return NAMES


"logging"


def level(loglevel="debug"):
    if loglevel != "none":
        os.environ["PYTHONUNBUFFERED"] = "yoo"
        format_short = "%(message)-80s"
        datefmt = '%H:%M:%S'
        logging.basicConfig(stream=sys.stderr, datefmt=datefmt, format=format_short)
        logging.getLogger().setLevel(LEVELS.get(loglevel))



def rlog(level, txt, ignore=None):
    if ignore is None:
        ignore = []
    for ign in ignore:
        if ign in str(txt):
            return
    logging.log(LEVELS.get(level), txt)


"utilities"


def debug(*args):
    for arg in args:
        sys.stderr.write(str(arg))
        sys.stderr.write("\n")
        sys.stderr.flush()


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    yeas = int(nsec/yea)
    nsec -= yeas*yea
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def spl(txt):
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = [txt, ]
    return [x for x in result if x]


"methods"


def fmt(obj, args=None, skip=None, plain=False):
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str):
            txt += f'{key}="{value}" '
        else:
            txt += f'{key}={value} '
    return txt.strip()


"data"


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'warn': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
         }


"interface"


def __dir__():
    return modules()
