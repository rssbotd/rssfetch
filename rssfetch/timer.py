# This file is placed in the Public Domain.


"timers"


import threading
import time


from .thread import launch, name


class Timy(threading.Timer):

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__(sleep, func)
        self.name      = kwargs.get("name", name(func))
        self.sleep     = sleep
        self.state     = {}
        self.starttime = time.time()


class Timed:

    def __init__(self, sleep, func, *args, thrname="", **kwargs):
        self.args   = args
        self.func   = func
        self.kwargs = kwargs
        self.sleep  = sleep
        self.name   = thrname or kwargs.get("name", name(func))
        self.target = time.time() + self.sleep
        self.timer  = None

    def run(self):
        self.timer.latest = time.time()
        self.func(*self.args)

    def start(self):
        self.kwargs["name"] = self.name
        timer = Timy(self.sleep, self.run, *self.args, **self.kwargs)
        timer.state["latest"] = time.time()
        timer.state["starttime"] = time.time()
        timer.start()
        self.timer   = timer

    def stop(self):
        if self.timer:
            self.timer.cancel()


class Repeater(Timed):

    def run(self) -> None:
        launch(self.start)
        super().run()


def __dir__():
    return (
        'Repeater',
        'Timed'
    )
