import zipfile
import tarfile
from threading import Thread
import time
from watchdog.events import *
from watchdog.observers import Observer
import json
import os
from . import function
import re


class JsonConfig(object):
    _tm = None

    def __init__(self, path, **kwargs):
        if path[0] == "/":
            self._path = path
        else:
            self._path = os.getcwd().replace("\\", "/")+"/"+path

        self._dict = dict()
        for key in dir(self.__class__):
            value = getattr(self.__class__, key)
            if key[0] != "_":
                json.dumps(value)
                self._dict[key] = value
        try:
            with open(self._path, "r") as f:
                d = json.loads(f.read())
                self._dict.update(d)
                self._dict.update(kwargs)
        except:
            function.write(self._path, self._dict)
        self._tm = os.path.getmtime(path)

    def __setattr__(self, key, value):

        if key[0] != "_":
            if value != self._dict[key]:
                self._dict[key] = value
                function.write(self._path, self._dict)
                self._tm = os.path.getmtime(self._path)
                # print("write", self._path, key, value, self._dict)
        super().__setattr__(key, value)

    def _async_read(self):
        if os.path.getmtime(self._path) != self._tm:
            with open(self._path, "r") as f:
                self._dict.update(json.loads(f.read()))
            self._tm = os.path.getmtime(self._path)

    def __getattribute__(self, key):
        if key[0] != "_":
            self._async_read()
            return self._dict[key]
        return super().__getattribute__(key)


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, p):
        self._p = p
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        if self._p._on_file_change:
            self._p._on_file_change(self.pre(event))

    def pre(self, e):
        return dict(
            src_path=e.src_path.replace("\\", "/")
        )


class FileSystem():
    def __init__(self, src_path, check=None, filter=None):
        if isinstance(src_path, str):
            self._src_path = [src_path]
        else:
            self._src_path = src_path
        if check is None:
            check = []
        if filter is None:
            filter = []
        self._check = [re.compile(d) for d in check]
        self._filter = [re.compile(d) for d in filter]

    def files(self):
        rt = []
        for d in self._src_path:
            self.file_one(d, rt)
        return rt

    def check(self, p):
        for c in self._check:
            if not c.match(p):
                return False
        for c in self._filter:
            if c.match(p):
                return False
        return True

    def file_one(self, d, rt):
        if isinstance(d, FileSystem):
            rt += d.files()
            return
        if self.check(d):
            if os.path.isfile(d):
                rt.append(d)
            else:
                for p in os.listdir(d):
                    self.file_one(d+"/"+p, rt)
        return rt

    def zip(self, dstfile, p):
        zip_file = zipfile.ZipFile(dstfile, mode='w')
        for d in self.files():
            zip_file.write(d, p(d))
        zip_file.close()

    def pyinstaller(self, p, hide_cmd=True, icon="icon.ico"):
        name = p.replace(".py", "")
        aim = "dist/%s/%s.exe" % (name, name)
        if not os.path.exists(aim):
            cmds = ["pyinstaller"]
            if not hide_cmd:
                cmds.append("-w")
            if icon:
                cmds.append(icon)
            cmds.append(p)
            os.system(" ".join(cmds))

        self.copyfiles("dist/%s" % name)

    def copyfiles(self, dist):
        for d in self.files():
            with open(d, "rb") as f:
                function.writeFile(dist+"/"+d, f.read())


class FileWatch:
    _on_file_change = None

    def __init__(self, path):
        observer = Observer()
        event_handler = FileEventHandler(self)
        observer.schedule(event_handler, path, True)
        observer.start()

    def on_file_change(self, v):
        self._on_file_change = v
        return self


if __name__ == "__main__":
    FileSystem(
        "d:/project/blj/dist",
        filter=[r".*\.bak"]
    ).zip("temp/blj.zip", lambda v: v.replace("d:/project/blj/dist/", ""))
