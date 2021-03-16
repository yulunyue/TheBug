from common.filehander import FileWatch, JsonConfig
from common import function
import time
import json


class TestFileHander:
    def test_watch(self):
        path = "temp/text.text"
        pathwatch = [None]

        def v(event):
            pathwatch[0] = event['src_path']
        self.file_watch = FileWatch("test").on_file_change(v)
        with open(path, "w") as f:
            f.write("??")
        time.sleep(0.2)
        assert pathwatch[0] == path

    def test_file_json(self):
        p = "temp/temp/a.json"

        class Tmp(JsonConfig):
            a = 0
            b = []
        c = Tmp(p)
        c.b.append("12")
        c.a = 1
        time.sleep(0.5)
        with open(p, "r") as f:
            d = json.loads(f.read())
            assert d['a'] == 1
            assert d["b"][0] == "12"
        function.write(p, json.dumps(dict(a=3)))
        assert c.a == 3
