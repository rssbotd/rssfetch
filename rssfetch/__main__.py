# This file is placed in the Public Domain.


"main program"


import os
import pathlib
import sys
import time
import _thread


from .event   import Event
from .modules import Commands, Main, command, inits
from .modules import md5sum, mods, level, modules, parse, rlog, scan, settable
from .serial  import dumps
from .paths   import Workdir, pidname
from .thread  import Errors, full


from .modules.rss import opml, shortid


"handler"


def handler(signum, frame):
    _thread.interrupt_main()


"output"


def out(txt):
    print(txt.rstrip())
    sys.stdout.flush()


"utilities"


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


def nodebug():
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())


def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)


def setwd(name, path=""):
    Main.name = name
    path = path or os.path.expanduser(f"~/.{name}")
    Workdir.wdr = path


"scripts"


def background():
    daemon("-v" in sys.argv)
    setwd(Main.name)
    privileges()
    pidfile(pidname(Main.name))
    settable()
    imp()
    inits(Main.init or "irc,rss")
    forever()


def service():
    setwd(Main.name)
    settable()
    level(Main.level or "none")
    imp()
    banner()
    privileges()
    pidfile(pidname(Main.name))
    inits(Main.init or "irc,rss")
    forever()


def imp():
    if len(sys.argv) < 2:
        out(f"{Main.name} <filename>")
        os._exit(0)
        return
    fnm = sys.argv[1]
    if not os.path.exists(fnm):
        out(f"no {fnm} file found.")
        os._exit(0)
        return
    nrs = opml(fnm)
    if nrs:
        out(f"added {nrs} urls.")


"runtime"


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


"main"


def main():
    if check("a"):
        Main.init = ",".join(modules())
    if check("v"):
        level("debug")
        setattr(Main.opts, "v", True)
    if check("d"):
        background()
    else:
        wrapped(service)


if __name__ == "__main__":
    main()
