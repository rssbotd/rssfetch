# This file is placed in the Public Domain.


"event handler"


import queue
import threading
import time
import _thread


from .objects import Object
from .runtime import launch


"handler"


class Handler:

    def __init__(self):
        self.lock = _thread.allocate_lock()
        self.cbs = {}
        self.queue = queue.Queue()
        self.ready = threading.Event()
        self.stopped = threading.Event()

    def available(self, event):
        return event.type in self.cbs

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            event._thr = launch(func, event)

    def loop(self):
        while not self.stopped.is_set():
            event = self.poll()
            if event is None:
                break
            event.orig = repr(self)
            self.callback(event)
        self.ready.set()

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, typ, cbs):
        self.cbs[typ] = cbs

    def start(self, daemon=True):
        self.stopped.clear()
        launch(self.loop, daemon=daemon)

    def stop(self):
        self.stopped.set()
        self.queue.put(None)
        self.ready.wait()

    def wait(self):
        pass


"event"


class Event(Object):

    def __init__(self):
        Object.__init__(self)
        self._ready  = threading.Event()
        self._thr    = None
        self.channel = ""
        self.ctime   = time.time()
        self.orig    = ""
        self.rest    = ""
        self.result  = {}
        self.type    = "event"
        self.txt     = ""

    def done(self):
        self.reply("ok")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        self._ready.wait()
        if self._thr:
            self._thr.join()


"interface"


def __dir__():
    return (
        'Handler',
        'Event'
    )
