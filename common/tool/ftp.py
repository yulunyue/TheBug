from typing import Dict, List
from os import error
from common import function, filehandel
from ftplib import FTP
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os
import time
import _thread


class FtpConfig(filehandel.JsonConfig):
    port = 55000
    username = "yly"
    password = "xykj20160315"
    src_ip = "127.0.0.1"
    dst_ip = "0.0.0.0"
    src_dir = "temp/ftpclient"
    remote_dir = "temp/ftpserver"


class FtpBase:
    def __init__(self, p, **kwargs):
        self.config = FtpConfig(p, **kwargs)
        self.init()

    def init(self):
        pass

    def run(self):
        pass

    def run_async(self):
        _thread.start_new_thread(self.run, ())


class FtpFile:
    def __init__(self, p, path):
        self._p = p
        self._config: FtpConfig = p.config
        self._path = path
        self._remote_modify = None
        self._local_modify = None
        self._remote_size = 0
        self._local_size = 0

    def remote_update(self, p):
        if self._remote_modify != p["modify"]:
            self._remote_modify = p["modify"]
            self._p.download(self._path)
            self._remote_size = p["size"]

    def local_update(self, p):
        if self._local_modify != p["modify"]:
            self._local_modify = p["modify"]
            self._p.upload(self._path)
            self._local_size = p["size"]


class FtpClient(FtpBase):
    def init(self):
        self._files_map: Dict[str, FtpFile] = dict()
        self.ftp = FTP()

    def run(self):
        while True:
            if self.connect():
                self.list_remote_dir()
                self.list_local_dir(self.config.src_dir)

    def list_remote_dir(self, path="", deepth=10):
        for name, param in self.ftp.mlsd(path):
            if path == "":
                file_path = name
            else:
                file_path = path+"/"+name
            if param["type"] == "dir":
                self.list_remote_dir(file_path, deepth - 1)
            else:
                if file_path not in self._files_map:
                    self._files_map[file_path] = FtpFile(self, file_path)
                self._files_map[file_path].remote_update(param)

    def list_local_dir(self, path):
        for name in os.listdir(path):
            file_path = path+"/"+name
            if os.path.isdir(file_path):
                self.list_local_dir(file_path)
            else:
                lpath = file_path.replace(self.config.src_dir, "")
                if lpath not in self._files_map:
                    self._files_map[lpath] = FtpFile(self, lpath)
                self._files_map[lpath].local_update(dict(
                    size=os.path.getsize(file_path),
                    modify=os.path.getmtime(file_path)
                ))

    def connect(self):
        if self.ftp.sock is None:
            try:
                self.ftp.connect(self.config.src_ip,
                                 self.config.port, timeout=2)
                self.ftp.login(self.config.username, self.config.password)
            except Exception as e:
                print('ftp connect fail', e, self.config.src_ip, self.config.port,
                      self.config.username, self.config.password)
                self.ftp.sock = None
                # raise Exception("error", e)
                return False
        return True

    def upload(self, lpath):
        with open(self.config.src_dir+"/"+lpath, 'rb') as f:
            self.ftp.storbinary("STOR %s" % lpath, f)
            # print('yly ftp uplaod', lpath, spath, eror)

    def download(self, path):
        lpath = self.config.src_dir+"/"+path
        function.writeFile(lpath+'.tmp', '404')
        with open(lpath+'.tmp', 'wb') as f:
            self.ftp.retrbinary("RETR %s" % path, f.write)
        os.replace(lpath+'.tmp', lpath)
        return True


class FtpServer(FtpBase):
    def init(self):
        self.authorizer = DummyAuthorizer()
        if not os.path.exists(self.config.remote_dir):
            os.mkdir(self.config.remote_dir)
        self.authorizer.add_user(self.config.username,
                                 self.config.password, self.config.remote_dir, perm='elradfmwMT')
        self.authorizer.add_anonymous(self.config.remote_dir)
        self.hander = FTPHandler
        self.hander.authorizer = self.authorizer
        self.hander.banner = "yly ftp lib"
        self.hander.passive_ports = range(55000, 60000)
        self.address = (self.config.dst_ip, self.config.port)
        self.server = FTPServer(self.address, self.hander)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

    def run(self):
        self.server.serve_forever()

    def close(self):
        self.server.close_all()


if __name__ == "__main__":
    server = FtpServer("temp/ftpserver.json", remote_dir="temp/ftpserver")
    server.run_async()
    # function.writeFile("temp/ftpserver/time.txt", "%s" % time.time())
    # function.writeFile("temp/ftpserver/data/time.txt", "%s" % time.time())

    # server.start()
    FtpClient("temp/ftpserver.json", src_dir="temp/ftpclient").run_async()
    server.server.close_all()
    # FtpServer("temp/ftpserver.json", remote_dir="temp/ftpserver").run_async()
    # server.run_async()
    input("exit")
