from http.server import HTTPServer, BaseHTTPRequestHandler
import _thread

ht = b'''
<html>
<body>402</body>
<script src="a.js"></script>
</html>
'''


class Handel(BaseHTTPRequestHandler):
    def do_GET(self):
        self.wfile.write(ht)


class A(HTTPServer):
    def get_request(self):
        a, b = self.socket.accept()
        return a, b

    def run(self):
        _thread.start_new_thread(self.serve_forever, ())
        while True:
            pass


A(("0.0.0.0", 80), Handel).run()
