# This file is placed in the Public Domain.


"handler"


import unittest


from rssfetch.event   import Event
from rssfetch.handler import Handler


def hello(event):
    event.reply("hello!")
    event.ready()


hdl = Handler()
hdl.register("hello", hello)
hdl.start()


class TestHandler(unittest.TestCase):

    def test_loop(self):
        e = Event()
        e.type = "hello"
        hdl.put(e)
        e.wait()
        self.assertTrue(True)
