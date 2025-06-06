# This file is placed in the Public Domain.


"clients"


import unittest


from rssfetch.client import Client
from rssfetch.event  import Event


def hello(event):
    event.reply("hello")
    event.ready()


clt = Client()
clt.register("hello", hello)
clt.start()


class TestHandler(unittest.TestCase):

    def test_loop(self):
        e = Event()
        e.type = "hello"
        clt.put(e)
        e.wait()
        self.assertTrue(True)
