# This file is placed in the Public Domain.


"errors"


import traceback

class Errors:

    name   = __file__.rsplit("/", maxsplit=2)[-2]
    errors = []


def full(exc):
    return "".join(
                   traceback.format_exception(
                                              type(exc),
                                              exc,
                                              exc.__traceback__
                                             )
                  )


def later(exc):
    Errors.errors.append(exc)


def line(exc):
    exctype, excvalue, trb = type(exc), exc, exc.__traceback__
    trace = traceback.extract_tb(trb)
    result = ""
    for i in trace:
        fname = i[0]
        if fname.endswith(".py"):
            fname = fname[:-3]
        linenr = i[1]
        plugfile = fname.split("/")
        mod = []
        for ii in list(plugfile[::-1]):
            mod.append(ii)
            if Errors.name in ii or "bin" in ii:
                break
        ownname = '.'.join(mod[::-1])
        if ownname.endswith("__"):
            continue
        if ownname.startswith("<"):
            continue
        result += f"{ownname}:{linenr} "
    del trace
    res = f"{exctype} {result[:-1]} {excvalue}"
    if "__notes__" in dir(exc):
        for note in exc.__notes__:
            res += f" {note}"
    return res


def __dir__():
    return (
        'Errors',
        'full',
        'later',
        'line'
    )
