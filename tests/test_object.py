# This file is placed in the Public Domain.


"objects"


import unittest


from rssfetch.object import Object, items, keys, update, values


import rssfetch.object


OBJECT  = Object()
PACKAGE = rssfetch.object
VALIDJSON = '{"test": "bla"}'


attrs1 = (
    'Object',
    'construct',
    'dumps',
    'items',
    'keys',
    'loads',
    'update',
    'values'
)


attrs2 = (
    '__doc__',
    '__lt__',
    '__init__',
    '__setattr__',
    '__ne__',
    '__delattr__',
    '__eq__',
    '__dir__',
    '__new__',
    '__iter__',
    '__reduce__',
    '__class__',
    '__module__',
    '__gt__',
    '__str__',
    '__init_subclass__',
    '__reduce_ex__',
    '__dict__',
    '__subclasshook__',
    '__le__',
    '__contains__',
    '__weakref__',
    '__ge__',
    '__sizeof__',
    '__getattribute__',
    '__format__',
    '__len__',
    '__getstate__',
    '__repr__',
    '__hash__'
)


class TestObject(unittest.TestCase):

    def test_attributes(self):
        okd = True
        for meth in attrs2:
            mth = getattr(OBJECT, meth, None)
            if mth is None:
                okd = meth
        self.assertTrue(okd)

    def test_constructor(self):
        obj = Object()
        self.assertTrue(type(obj), Object)

    def test_class(self):
        obj = Object()
        clz = obj.__class__()
        self.assertTrue("Object" in str(type(clz)))

    def test_delattr(self):
        obj = Object()
        obj.key = "value"
        del obj.key
        self.assertTrue("key" not in dir(obj))

    def test_dict(self):
        obj = Object()
        self.assertEqual(obj.__dict__, {})

    def test_fmt(self):
        obj = Object()
        self.assertEqual(format(obj), '{}')

    def test_format(self):
        obj = Object()
        self.assertEqual(format(obj), '{}')

    def test_getattribute(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(obj.__getattribute__("key"), "value")

    def test_getattr(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(getattr(obj, "key"), "value")

    def test_hash(self):
        obj = Object()
        hsj = hash(obj)
        self.assertTrue(isinstance(hsj, int))

    def test_init(self):
        obj = Object()
        self.assertTrue(type(Object.__init__(obj)), Object)

    def test_items(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(items(obj)),
            [
                ("key", "value"),
            ],
        )

    def test_keys(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(keys(obj)),
            [
                "key",
            ],
        )

    def test_len(self):
        obj = Object()
        self.assertEqual(len(obj), 0)

    def test_methods(self):
        okd = True
        for attr in attrs1:
            att = getattr(PACKAGE, attr, None)
            if not att:
                okd = attr
                break
        self.assertTrue(okd)

    def test_module(self):
        self.assertEqual(Object().__module__, "rssfetch.object")

    def test_register(self):
        obj = Object()
        setattr(obj, "key", "value")
        self.assertEqual(obj.key, "value")

    def test_repr(self):
        self.assertTrue(update(Object(), {"key": "value"}).__repr__(), {"key": "value"})

    def test_setattr(self):
        obj = Object()
        obj.__setattr__("key", "value")
        self.assertTrue(obj.key, "value")

    def test_str(self):
        obj = Object()
        self.assertEqual(str(obj), "{}")

    def test_update(self):
        obj = Object()
        obj.key = "value"
        oobj = Object()
        update(oobj, obj)
        self.assertTrue(oobj.key, "value")

    def test_values(self):
        obj = Object()
        obj.key = "value"
        self.assertEqual(
            list(values(obj)),
            [
                "value",
            ],
        )
