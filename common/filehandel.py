from threading import Thread
import time
from watchdog.events import *
from watchdog.observers import Observer
import json
import os
from . import function


class JsonConfig(object):
    def __init__(self, path):
        self._tm = os.path.getmtime(path)
        self._dict = dict()
        self._path = path
        for key in dir(self.__class__):
            value = getattr(self.__class__, key)
            if key[0] != "_":
                json.dumps(value)
                self._dict[key] = value
        try:
            with open(self._path, "r") as f:
                d = json.loads(f.read())
                self._dict.update(d)
        except:
            function.write(self._path, self._dict)

    def __setattr__(self, key, value):
        if key[0] != "_" and value != self._dict[key]:
            self._dict[key] = value
            function.write(self._path, self._dict)
            self._tm = os.path.getmtime(self._path)
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
    pass
