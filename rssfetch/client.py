# This file is placed in the Public Domain.


"client"


from .fleet   import Fleet
from .handler import Handler


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        Fleet.add(self)

    def announce(self, txt):
        pass

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


def __dir__():
    return (
        'Client',
    )
