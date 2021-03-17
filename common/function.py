import traceback
import json
import os
import time


class Base:
    def append(self, *args):
        for d in args:
            if isinstance(d, list):
                if isinstance(d[-1], dict):
                    self.append_one(*d[:-1], **d[-1])
                else:
                    self.append_one(*d)
            elif isinstance(d, dict):
                self.append_one(**d)
            else:
                self.append_one(d)
        return self

    def append_one(self, *args, **kwargs):
        pass


def dirs(v, check=None):
    rt = dict()
    for d in dir(v):
        if d[0] != "_":
            v1 = getattr(v, d)
            if check is None or check(v1):
                rt[d] = v1
    return rt


def mkfiledir(p):
    path = ""
    for d in p.split('/')[:-1]:
        if path == "":
            path += d
        else:
            path += '/'+d
        if not os.path.exists(path):
            os.mkdir(path)


def writeFile(p, v):
    if not os.path.exists(p):
        mkfiledir(p)
    with open(p, "wb") as f:
        if isinstance(v, str):
            f.write(v.encode())
        else:
            f.write(v)


def write(path, v):
    if isinstance(v, dict):
        v = json.dumps(v, indent=4)
    if isinstance(path, str):
        c = path.split(":")
        if len(c) == 1:
            return writeFile(c[0], v)


def now_str(time_stamp=None, formats="%Y-%m-%d %H:%M:%S"):
    tail = ""
    if time_stamp is None:
        time_stamp = time.time()
    if '.%f' in formats:
        formats = formats.replace('.%f', '')
        tail = ".%s" % (int(time_stamp*1000) % 1000)
    if time_stamp < 0:
        dt = datetime(
            1970, 1, 1) + timedelta(seconds=time_stamp)
        return formats.replace(
            "%Y", str(dt.year)
        ).replace(
            '%M', str(dt.month)
        ).replace(
            '%d', str(dt.day)
        ).repalce(
            '%H', str(dt.hour)
        ).replace(
            '%M', str(dt.minute)
        ).replace(
            '%S', str(dt.seconds)
        )
    return time.strftime(formats, time.localtime(time_stamp))+tail


def log(*args):
    print(now_str(formats="%H:%M:%S.%f"), *args)


def forerver(p):
    while True:
        try:
            p()
        except Exception as e:
            log("forerver error", e)
            traceback.print_exc()
            break
