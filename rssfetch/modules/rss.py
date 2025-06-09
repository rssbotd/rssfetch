# This file is placed in the Public Domain.


"rich site syndicate"


import html
import html.parser
import http.client
import re
import urllib
import urllib.parse
import urllib.request
import uuid
import _thread


from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode


from ..cache  import Cache, find, getpath
from ..fleet  import Fleet
from ..object import Object, update
from ..thread import Repeater, launch
from .        import Default, rlog, spl


DEBUG = False


fetchlock  = _thread.allocate_lock()
importlock = _thread.allocate_lock()


errors     = []
skipped    = []


class Urls(Default):

    pass


seen = Urls()


def init():
    fetcher = Fetcher()
    fetcher.start()
    return fetcher


class Rss(Default):

    def __init__(self):
        Default.__init__(self)
        self.display_list = 'title,link,author'
        self.insertid     = None
        self.name         = ""
        self.rss          = ""


class Feed(Default):

    def __init__(self):
        Default.__init__(self)
        self.name = ""



class Fetcher(Object):

    def __init__(self):
        self.dosave = False

    @staticmethod
    def display(obj):
        result = ''
        displaylist = []
        try:
            displaylist = obj.display_list or 'title,link'
        except AttributeError:
            displaylist = 'title,link,author'
        for key in displaylist.split(","):
            if not key:
                continue
            data = getattr(obj, key, None)
            if not data:
                continue
            data = data.replace('\n', ' ')
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += ' - '
        return result[:-2].rstrip()

    def fetch(self, feed, silent=False):
        with fetchlock:
            result = []
            see = getattr(seen, feed.rss, [])
            urlz = []
            counter = 0
            for obj in reversed(getfeed(feed.rss, feed.display_list)):
                counter += 1
                fed = Feed()
                update(fed, obj)
                update(fed, feed)
                url = urllib.parse.urlparse(fed.link)
                if url.path and not url.path == '/':
                    uurl = f'{url.scheme}://{url.netloc}/{url.path}'
                else:
                    uurl = fed.link
                urlz.append(uurl)
                if uurl in see:
                    continue
                result.append(fed)
            setattr(seen, feed.rss, urlz)
        if silent:
            return counter
        txt = ''
        feedname = getattr(feed, 'name', None)
        if feedname:
            txt = f'[{feedname}] '
        for obj in result:
            txt2 = txt + self.display(obj)
            for bot in Fleet.clients.values():
                bot.announce(txt2)
        return counter

    def run(self, silent=False):
        thrs = []
        for _fn, feed in find('rss'):
            thrs.append(launch(self.fetch, feed, silent))
        return thrs

    def start(self):
        repeater = Repeater(300.0, self.run)
        repeater.start()


class OPML:

    @staticmethod
    def getnames(line):
        return [x.split('="')[0]  for x in line.split()]

    @staticmethod
    def getvalue(line, attr):
        lne = ''
        index1 = line.find(f'{attr}="')
        if index1 == -1:
            return lne
        index1 += len(attr) + 2
        index2 = line.find('"', index1)
        if index2 == -1:
            index2 = line.find('/>', index1)
        if index2 == -1:
            return lne
        lne = line[index1:index2]
        if 'CDATA' in lne:
            lne = lne.replace('![CDATA[', '')
            lne = lne.replace(']]', '')
            #lne = lne[1:-1]
        return lne

    @staticmethod
    def getattrs(line, token):
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = line.find(f'<{token} ', index)
            if index1 == -1:
                return result
            index1 += len(token) + 2
            index2 = line.find('/>', index1)
            if index2 == -1:
                return result
            result.append(line[index1:index2])
            index = index2
        return result

    @staticmethod
    def parse(txt, toke="outline", itemz=None):
        if itemz is None:
            itemz = ",".join(OPML.getnames(txt))
        result = []
        for attrz in OPML.getattrs(txt, toke):
            if not attrz:
                continue
            obj = Object()
            for itm in spl(itemz):
                if itm == "link":
                    itm = "href"
                val = OPML.getvalue(attrz, itm)
                if not val:
                    continue
                if itm == "href":
                    itm = "link"
                setattr(obj, itm, val.strip())
            result.append(obj)
        return result


class Parser:

    @staticmethod
    def getitem(line, item):
        lne = ''
        index1 = line.find(f'<{item}>')
        if index1 == -1:
            return lne
        index1 += len(item) + 2
        index2 = line.find(f'</{item}>', index1)
        if index2 == -1:
            return lne
        lne = line[index1:index2]
        lne = cdata(lne)
        return lne.strip()

    @staticmethod
    def getitems(text, token):
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = text.find(f'<{token}', index)
            if index1 == -1:
                break
            index1 += len(token) + 2
            index2 = text.find(f'</{token}>', index1)
            if index2 == -1:
                break
            lne = text[index1:index2]
            result.append(lne)
            index = index2
        return result

    @staticmethod
    def parse(txt, toke="item", items='title,link'):
        result = []
        for linez in Parser.getitems(txt, toke):
            linez = linez.strip()
            obj = Object()
            for itm in spl(items):
                val = Parser.getitem(linez, itm)
                if val:
                    val = unescape(val.strip())
                    val = val.replace("\n", "")
                    val = striphtml(val)
                    setattr(obj, itm, val)
            result.append(obj)
        return result


def attrs(obj, txt):
    update(obj, OPML.parse(txt))


def cdata(lne):
    if 'CDATA' in lne:
        ln = lne.replace('![CDATA[', '')
        ln = ln.replace(']]', '')
        ln = ln[1:-1]
        return ln
    return lne


def getfeed(url, items):
    result = [Object(), Object()]
    if DEBUG:
        return result
    try:
        rest = geturl(url)
    except (http.client.HTTPException, ValueError, HTTPError, URLError) as ex:
        txt = f"{url} {ex}"
        if txt not in errors:
            rlog("error", txt)
            errors.append(txt)
        return result
    if rest:
        if url.endswith('atom'):
            result = Parser.parse(str(rest.data, 'utf-8'), 'entry', items) or []
        else:
            result = Parser.parse(str(rest.data, 'utf-8'), 'item', items) or []
    return result


def gettinyurl(url):
    postarray = [
        ('submit', 'submit'),
        ('url', url),
    ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = urllib.request.Request('http://tinyurl.com/create.php',
                  data=bytes(postdata, 'UTF-8'))
    req.add_header('User-agent', useragent("rss fetcher"))
    with urllib.request.urlopen(req) as htm: # nosec
        for txt in htm.readlines():
            line = txt.decode('UTF-8').strip()
            i = re.search('data-clipboard-text="(.*?)"', line, re.M)
            if i:
                return i.groups()
    return []


def geturl(url):
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(str(url))
    req.add_header('User-agent', useragent("rss fetcher"))
    with urllib.request.urlopen(req) as response: # nosec
        response.data = response.read()
        return response


def opml(path):
    with open(path, "r", encoding="utf-8") as file:
        txt = file.read()
    prs = OPML()
    nrs = 0
    nrskip = 0
    insertid = shortid()
    with importlock:
        for obj in prs.parse(txt, 'outline', "name,display_list,xmlUrl"):
            url = obj.xmlUrl
            if url in skipped:
                continue
            if not url.startswith("http"):
                continue
            has = list(find("rss", {'rss': url}, matching=True))
            if has:
                skipped.append(url)
                nrskip += 1
                continue
            rss = Rss()
            update(rss, obj)
            rss.rss = obj.xmlUrl
            rss.insertid = insertid
            Cache.add(getpath(rss), rss)
            nrs += 1
    return nrs + nrskip


def shortid():
    return str(uuid.uuid4())[:8]


def striphtml(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def sync():
    fetcher = Fetcher()
    thrs = fetcher.run(True)
    nrs = 0
    for thr in thrs:
        thr.join()
        nrs += 1
    return nrs


def unescape(text):
    txt = re.sub(r'\s+', ' ', text)
    return html.unescape(txt)


def useragent(txt):
    return 'Mozilla/5.0 (X11; Linux x86_64) ' + txt
