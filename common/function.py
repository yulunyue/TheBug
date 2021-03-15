import json
import os


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
        f.write(v.encode())


def write(path, v):
    if isinstance(v, dict):
        v = json.dumps(v, indent=4)
    if isinstance(path, str):
        c = path.split(":")
        if len(c) == 1:
            return writeFile(c[0], v)
