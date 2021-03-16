from common.io import IoManage, TcpC, TcpS, UdpC, UdpS
from
import time


class TestIo:
    _io_instance = IoManage().run_by_thread()

    def test_tcp(self):
        self.index = 0
        value = [None, None]

        def readc(p, d):
            # print("p",d)
            value[0] = d

        def reads(p, d):
            value[1] = d
            return "s"
        self._io_instance.append(
            TcpS("0.0.0.0", 503, hock_read=reads),
            TcpC("127.0.0.1", 503, hock_read=readc, key="key")
        )
        time.sleep(0.1)
        self._io_instance.writeData("key", b'b')
        time.sleep(0.1)
        assert value[0] == b's' and value[1] == b'b'

    def test_ftp(self):
        self._io_instance.append(
            ["ftpserver", "temp/ftpserver.json",
                dict(rootdir="temp/ftpclient")],
            ["ftpclient", "temp/ftpclient.json",
                dict(rootdir="temp/ftpserver")]
        )
