# This file is placed in the Public Domain.


"main"


import os
import pathlib
import sys
import time



from .clients import Client
from .command import Main, Commands, command, inits, parse, scan
from .handler import Event
from .imports import modules
from .persist import Workdir, pidname, skel, types
from .runtime import level
from .modules import rss


Main.modpath = os.path.dirname(rss.__file__)
Main.name = Main.__module__.split(".")[0]


def out(txt):
    print(txt)
    sys.stdout.flush()


class CLI(Client):

    def __init__(self):
        Client.__init__(self)
        self.register("command", command)

    def raw(self, txt):
        out(txt.encode('utf-8', 'replace').decode("utf-8"))


class Console(CLI):

    def announce(self, txt):
        #out(txt)
        pass

    def callback(self, evt):
        super().callback(evt)
        evt.wait()

    def poll(self):
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


"utilities"


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    out(f"{Main.name.upper()} {Main.version} since {tme} ({Main.level.upper()})")
    out(f"loaded {".".join(modules(Main.modpath))}")


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


def forever():
    while True:
        try:
            time.sleep(0.01)
        except (KeyboardInterrupt, EOFError):
            sys.exit(1)


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
    skel()


"commands"


def cmd(event):
    event.reply(",".join(sorted([x for x in Commands.names if x not in Main.ignore])))


def ls(event):
    event.reply(",".join([x.split(".")[-1].lower() for x in types()]))


def srv(event):
    import getpass
    name = getpass.getuser()
    event.reply(TXT % (Main.name.upper(), name, name, name, Main.name))


"scripts"


def background():
    daemon("-v" in sys.argv)
    privileges()
    level(Main.level or "debug")
    setwd(Main.name)
    pidfile(pidname(Main.name))
    Commands.add(cmd)
    scan(Main.modpath)
    inits(Main.init or "irc,rss")
    forever()


def console():
    import readline # noqa: F401
    parse(Main, " ".join(sys.argv[1:]))
    Main.init = Main.sets.init or Main.init
    Main.verbose = Main.sets.verbose or Main.verbose
    Main.level   = Main.sets.level or Main.level or "warn"
    level(Main.level)
    setwd(Main.name)
    Commands.add(cmd)
    Commands.add(ls)
    scan(Main.modpath)    
    if "v" in Main.opts:
        banner()
    for _mod, thr in inits(Main.init):
        if "w" in Main.opts:
            thr.join(30.0)
    csl = Console()
    csl.start()
    forever()


def control():
    if len(sys.argv) == 1:
        return
    parse(Main, " ".join(sys.argv[1:]))
    level(Main.level or "debug")
    setwd(Main.name)
    Commands.add(cmd)
    Commands.add(ls)
    Commands.add(srv)
    scan(Main.modpath)
    csl = CLI()
    evt = Event()
    evt.orig = repr(csl)
    evt.type = "command"
    evt.txt = Main.otxt
    command(evt)
    evt.wait()


def service():
    level(Main.level or "warn")
    setwd(Main.name)
    banner()
    privileges()
    pidfile(pidname(Main.name))
    Commands.add(cmd)
    scan(Main.modpath)
    inits(Main.init or "irc,rss")
    forever()


"data"


TXT = """[Unit]
Description=%s
After=network-online.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%s -s

[Install]
WantedBy=multi-user.target"""



"runtime"


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        out("")


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
    if check("a"):
        Main.init = ",".join(modules(Main.modpath))
    if check("v"):
        setattr(Main.opts, "v", True)
    if check("c"):
        wrap(console)
    elif check("d"):
        background()
    elif check("s"):
        wrapped(service)
    else:
        wrapped(control)


if __name__ == "__main__":
    main()
