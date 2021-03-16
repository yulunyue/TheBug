from common import function
import _thread
import socket
import json
from typing import Dict, List
import time
import asyncio
import sys
import traceback


class IoManage(function.Base):
    clsMap = dict()
    _ioinstance = None

    def __init__(self, on_read=None):
        self.clients = {}
        self.client_array=[]
        self.read = on_read
        self._on_close_connection = None
        self._on_new_connection = None
    def __new__(cls):
        if cls._ioinstance:
            return cls._ioinstance
        cls._ioinstance=super().__new__(cls)
        return cls._ioinstance
    def append_one(self,cls,*args,**kwargs):
        if isinstance(cls, str):
            cls = self.clsMap[cls]
            v = cls(*args,**kwargs)
        else:
            v=cls
        v.p=self
        v.index=len(self.client_array)
        self.client_array.append(v)
        if v.key is None:
            v.key = "%s_%s"%(v.proto,len(self.client_array))
        self.clients[v.key]=v
        return v

    def remove(self, io):
        del self.clients[io.key]
        self.client_array.pop(io.index)


    async def server_forever(self, loopt=0.01):
        while True:
            for c in self.client_array:
                # print(key, 'run')
                await c.run()
            await asyncio.sleep(loopt)

    def run(self):
        asyncio.run(self.server_forever())
        return self
    def run_by_thread(self):
        _thread.start_new_thread(self.run,())
        return self
    # def dump(self):
    #     node = {}
    #     config = {}
    #     for key in self.clients:
    #         node[key] = self.clients[key].redirectList
    #         config[key] = self.clients[key].dump()
    #     return [node, config]

    def search(self, srcip, srcport, proto):
        for key in self.clients:
            d = self.clients[key]
            if d.srcip == srcip and d.srcport == srcport and d.proto == proto:
                return d

    def on_read(self, key, data):
        # print("iomange", self.read)
        if self.read:
            self.read(key, data)

    def on_new_connection(self, tp, *args):
        if self._on_new_connection:
            self._on_new_connection(tp, *args)

    def on_close_connection(self, tp, *args):
        if self._on_close_connection:
            self._on_close_connection(tp, *args)

    def writeData(self,key,data):
        self.clients[key].writeData(data)

        
class IoInstance:
    p: IoManage = None
    proto = ''
    index=0
    def __init__(self,  key=None, hock_read=None,redirectList=None,sock=None):
        self.key = key
        self.redirectList = redirectList or []
        self.hock_read=hock_read
        self.buff = None
        self.connectnum = 0
        self.sock=sock
    def getdefaultkey(self):
        f = "%s:%s:%s"
        if self.serverorclient == 0:
            return f % (self.__class__.__name__, self.srcip, self.srcport)
        else:
            return f % (self.__class__.__name__, self.dstip, self.dstport)

    def check(self):
        ip, port = self.srcip, self.srcport
        if self.serverorclient == 1:
            ip, port = self.dstip, self.dstport
        if port < 0 or port > 65535:
            return False
        try:
            if any([int(d) > 255 or int(d) < 0 for d in ip.split('.')]):
                return False
        except Exception as e:
            return False
        return True

    def log(self, *args):
        if 'io.log' in sys.argv:
            pt = []
            for d in args:
                if isinstance(d, (bytes, bytearray)):
                    pt.append("%s:[" % len(d) +
                              " ".join(["%02x" % d2 for d2 in d])+"]")
                else:
                    pt.append(str(d))
            print(*pt)

    def write(self, data):
        pass
        # print('write',self.key,data)
    def writeData(self,data):
        if isinstance(data,str):
            data=data.encode()
        return self.write(data)
    async def run(self):
        pass

    def error(self,v=True):
        if v:
            self.sock = None
        # if 'io.error' in sys.argv:
        traceback.print_exc()
        # self.log('error', *args)

    def on_read(self, data):
        self.buff = data
        rt = None
        try:
            if self.hock_read:
                rt = self.hock_read(self, data)
            else:
                rt = self.p.on_read(self, data)
        except Exception as e:
            self.error(False)
        if rt:
            self.writeData(rt)
        # self.log("on_read", self.buff, rt, self.redirectList)
        # self.p.write(self.redirectList, data)





class TcpS(IoInstance):
    proto = 'tcps'
    def __init__(self,srcip,srcport,**kwargs):
        self.srcip=srcip
        self.srcport=srcport
        self.childs=[]
        super().__init__(**kwargs)
    async def run(self):
        if self.sock is None:
            if self.connectnum % 100 != 0:
                return
            self.connectnum = (self.connectnum+1) % 1000
            try:
                if self.srcip == '127.0.0.1':
                    self.srcip = '0.0.0.0'
                print('tcp server', self.srcip, self.srcport)
                self.sock = await asyncio.start_server(self.on_concat, self.srcip, self.srcport)
            except Exception as e:
                self.error()

    async def on_concat(self, r, w):
        srcip, srcport = w.get_extra_info('peername')
        self.p.on_new_connection("tcp", srcip, srcport)
        try:
            c = TcpC(self.srcip,self.srcport,srcip=srcip,srcport=srcport,hock_read=self.hock_read,
                            sock=(r, w),
                            key="%s_c%s" % (self.key, len(self.childs)),
                            redirectList=self.redirectList)
            self.p.append_one(c)
            self.childs.append(c)
            print('on_tcp_concet', srcip, srcport)
            await c.read()
        except Exception as e:
            self.error()
        # self.childs.append(c)
       
       
        

    def write(self, data):
        i = 0
        # num = len(self.childs)
        # print('tcpwrite',num)
        while i < len(self.childs):
            d = self.childs[i]
            if d.write(data):
                i += 1
            else:
                self.childs.pop(i)
                self.p.remove(d)
        return i


class TcpC(IoInstance):
    proto = 'tcpc'
    def __init__(self,dstip,dstport,srcip="127.0.0.1",srcport=0,**kwargs):
        self.srcip=srcip
        self.srcport=srcport
        self.dstip=dstip
        self.dstport=dstport
        super().__init__(**kwargs)
    async def asyncreadrw(self, r, w):
        try:
            data = await r.read(2048)
            if data:
                self.on_read(data)
                asyncio.create_task(self.asyncreadrw(r, w))
            else:
                self.p.on_close_connection("tcp", self.srcip, self.srcport)
                w.close()
        except Exception as e:
            w.close()
            self.p.on_close_connection("tcp", self.srcip, self.srcport)
            self.error()

    async def run(self):
        # print(self.sock,self.dstport)
        if self.sock is None:
            if self.dstport and self.dstip:
                try:
                    self.sock = await asyncio.open_connection(self.dstip, self.dstport)
                    # print("tcp connected",self.sock)
                    r, w = self.sock
                    # self.updateinfoByW(w)
                    asyncio.create_task(self.asyncreadrw(r, w))
                except Exception as e:
                    self.error()

    async def read(self):
        if self.sock:
            await self.asyncreadrw(*self.sock)

    def write(self, data):
        if self.sock:
            # print('write',self.key,data)
            try:
                r, w = self.sock
                w.write(data)
                self.log("tcpcwrite", data)
                return w._transport._conn_lost < 3
            except Exception as e:
                self.error()
                w.close()
                return False
    def __str__(self):
        return 'tcpc:%s->%s,%s,%s'%(self.key,self.dstip,self.dstport,self.srcport)

class UdpS(IoInstance):
    proto = 'udps'
    w = None
    serverorclient = 0

    async def run(self):
        if self.sock is None:
            if self.connectnum % 1000 != 0:
                return
            self.connectnum = (self.connectnum+1) % 1000
            try:
                loop = asyncio.get_running_loop()
                self.sock = await loop.create_datagram_endpoint(
                    self.udpread,
                    local_addr=(self.srcip, self.srcport),
                    remote_addr=(self.dstip, self.dstport)
                )
            except Exception as e:
                self.error()

    def udpread(self, *args):
        class Ep():
            def __init__(self, p):
                self.p: IoInstance = p

            def error_received(self, exc):
                print('udperror', exc)
                # p.sock=None

            def connection_made(self, transport):
                self.p.updateinfoByW(transport)
                num = len(self.p.childs)
                peername = transport.get_extra_info('peername')
                sockname = transport.get_extra_info('sockname')
                print('on_udp_conect', sockname, peername, num)
                # self.p.childs.append(
                #     self.p.p.append(UdpC,[],
                #     dict(
                #         sock=(self.p,self),
                #         key="%s_c%s"%(self.p.key,num)
                #     ))
                # )
                if peername and peername[1] != 0 and peername not in self.p.childs:
                    self.p.childs.append(peername)
                self.transport = transport

            def datagram_received(self, data, addr):
                if addr not in self.p.childs:
                    self.p.childs.append(addr)
                self.p.on_read(data)

        self.w = Ep(self)
        return self.w

    def write(self, data):
        try:
            for addr in self.childs:
                self.w.transport._sock.sendto(data, addr)
            return True
        except Exception as e:
            self.log('udpsenderror', e)
            return False


class UdpC(UdpS):
    serverorclient = 1


class Com(IoInstance):
    protp = 'udp'
    srcip_map = dict()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # print("__init__", self.srcip, self.srcport)
        # self.check()

    def write(self, data):
        # print('writecom', data)
        self.sock.write(data)
        # self.buff = p
        # if p and self.hock_read:
        #     self.hock_read(self, p)
        return True

    def check(self):
        from common.server import SerialClient
        try:
            self.sock = SerialClient(
                self.srcip, self.srcport, read=self.on_read, stopbit=2)
            if self.sock.open():
                self.sock.start()
            return True
        except Exception as e:
            self.sock = None
            self.error(e)
            return False

    def getdefaultkey(self):
        return "%s:%s" % (self.__class__.__name__, self.srcip)

IoManage.clsMap = dict(TcpC=TcpC, TcpS=TcpS, UdpS=UdpS, UdpC=UdpC,Com=Com)
