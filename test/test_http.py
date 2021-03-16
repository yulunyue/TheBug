import requests
import json
from common.httpsimple import run_thread, HttpApplication, BaseWeb


class Env(BaseWeb):
    def envdata(self, **kwargs):
        kwargs["file"] = len(kwargs["file"])
        rt = dict(
            path=self.env.path
        )
        rt.update(kwargs)
        return rt


class TestHttp:
    url = "http://127.0.0.1:90/test"
    run_thread(90, HttpApplication([
        ["/test", Env],
        ['/test/js/(.*)', lambda b, v, **kg:v+"123"]
    ]))

    def test_get(self):
        a = requests.get(self.url+"notfind").content
        print(a)
        assert a[0:3] == b'404'

    def test_re(self):
        assert requests.get(self.url+"/js/abc").content == b'abc123'

    def test_post(self):
        fname = "test/text.txt"
        v = json.loads(requests.post(
            self.url+"/envdata?a=1&b=2",
            data=dict(a=2),
            files={"file": (fname, open(fname, "rb"))}
        ).content)
        assert type(v).__name__ == "dict"
        assert v["msg"] == ""
        assert v["path"] == "/test/envdata"
        assert v["a"] == "2"
