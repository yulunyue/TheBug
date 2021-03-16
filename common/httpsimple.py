import json
from http.server import BaseHTTPRequestHandler, HTTPStatus,HTTPServer
from .application import Application, UtilClassCall
import _thread


class HttpHander(BaseHTTPRequestHandler):
    app = None

    def __init__(self, *args, **kwargs):
        self.params = dict()
        super().__init__(*args, **kwargs)

    def pre(self):
        p = self.path.split("?")
        if len(p) == 1:
            self.path = p[0]
        else:
            self.path = p[0]
            for d in p[1].split("&"):
                keys = d.split("=")
                if len(keys) >= 2:
                    self.params[keys[0]] = keys[1]

    def do_GET(self):
        try:
            self.pre()
            data = self.app.call(self)
        except Exception as e:
            data = str(e)
        self.out(data)

    def do_POST(self):
        try:
            self.pre()
            self.post_data()
            data = self.app.call(self)
            if isinstance(data, dict):
                if "statu" not in data:
                    data["statu"] = 200
                if "msg" not in data:
                    data["msg"] = ""
        except Exception as e:
            data = dict(statu=500, msg=str(e))
        self.out(data)

    def post_data(self):
        tp = self.headers["Content-Type"].split(";")[0]
        if tp == "application/json":
            data = json.loads(self.rfile.read(
                int(self.headers["content-length"])).decode())
            self.params.update(data)
        elif tp == "multipart/form-data":
            import cgi
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers["Content-Type"]
            })
            for key in form.keys():
                self.params[key] = form[key].value
            # raise Exception(str(list(form.keys())))
        else:
            raise Exception("error Content-Type %s" % tp)

    def out(self, d):
        if isinstance(d, (dict, list)):
            d = json.dumps(d)
        if isinstance(d, str):
            d = d.encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "html")
        self.send_header("Content-Length", "%s" % len(d))
        self.end_headers()
        # self.send_header("Last-Modified",
        # try:
        self.wfile.write(d)
        # except:
        #     pass


class HttpApplication(Application):

    def call(self, env):
        self.env: HttpHander = env
        key = env.path
        if key not in self._map_dict:
            return self.notfind()
        b = self._map_dict[key]
        if isinstance(b, UtilClassCall):
            b._oj.env = env
            return b.call(**env.params)
        return b()

    def notfind(self):
        for d in self._re_array:
            p = d[0].match(self.env.path)
            # print(d[0],self.env.path)
            if p:
                return d[1](self.env, p.groups()[0], **self.env.params)
        if self.env.command == "GET":
            return '404'+"->"+self.env.path
        else:
            return dict(statu=404, msg="not find %s->%s" % (self.env.path, list(self._map_dict.keys())))


class BaseWeb:
    env: HttpHander


def hendermake(v):
    class Tmp(HttpHander):
        pass
    Tmp.app = v
    return Tmp


def run(port, hande):

    hander = hendermake(hande)
    HTTPServer(("", port), hander).serve_forever()


def run_thread(*args):
    _thread.start_new_thread(run, args)
