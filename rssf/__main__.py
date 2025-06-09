# This file is placed in the Public Domain.


"main program"


import os
import sys
import time
import _thread


from .modules import Main, inits, level, parse
from .thread  import Errors, full


from .modules.rss import opml, sync


def background():
    daemon("-v" in sys.argv)
    privileges()
    fnm = checkargs()
    banner()
    opml(fnm)
    sync()
    inits("irc,rss")
    forever()


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    out(f"{Main.name.upper()} since {tme} ({Main.level.upper()})")


def check(txt):
    args = sys.argv[1:]
    for arg in args:
        if not arg.startswith("-"):
            continue
        for char in txt:
            if char in arg:
                return True
    return False


def checkargs():
    if len(sys.argv) < 2:
        out(f"{Main.name} <filename>")
        os._exit(0)
    fnm = sys.argv[1]
    if not os.path.exists(fnm):
        out(f"no {fnm} file found.")
        os._exit(0)
    return fnm


def daemon(verbose=False):
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 != 0:
        os._exit(0)
    if not verbose:
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as sos:
            os.dup2(sos.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as ses:
            os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    os.nice(10)


def errors():
    for exc in Errors.errors:
        out(full(exc))


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


def out(txt):
    print(txt.rstrip())
    sys.stdout.flush()


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)


def service():
    parse(Main, " ".join(sys.argv[1:]))
    level(Main.level)
    fnm = checkargs()
    banner()
    opml(fnm)
    nrs = sync()
    out(f"{nrs} feeds synced")
    privileges()
    inits("irc,rss")
    forever()


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        out("")
    errors()


def wrap(func):
    import termios
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        wrapped(func)
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


def main():
    if check("v"):
        level("debug")
        setattr(Main.opts, "v", True)
    if check("d"):
        background()
    else:
        wrapped(service)


if __name__ == "__main__":
    main()
