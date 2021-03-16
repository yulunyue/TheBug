import sys
from common.model import Base, Integer, Column, String, MyDb, Float, Session, ForeignKey, relationship, Text
from typing import List, Dict
import time
from common import function


class BljRecord(Base):
    __tablename__ = "blj_record"
    coatingType = Column(String(512), default="xxx", info=dict(
        index=2, label="Coating Type", type="select"))
    peerSpeed = Column(String(512), default="10",
                       info=dict(index=4, label="Peel Speed"))
    testNumber = Column(String(512), default="",
                        info=dict(index=1, label="Test No"))
    peerAngle = Column(String(512), default="10", info=dict(
        index=5, label="Peel angle"
    ))
    username = Column(String(512), default="", info=dict(
        index=15, label="Tester"
    ))
    peer_number = Column(String(512), default="", info=dict(
        index=8, label="Pipe No or Joint Coating No"
    ))
    peer_position = Column(String(512), default="", info=dict(
        index=9, label="Peel Position"
    ))
    test_temperature = Column(String(512), default="", info=dict(
        index=12, label="Temp Control"
    ))
    failureMode = Column(String(512), default="")
    testStandard = Column(String(512), default="", info=dict(
        index=3, label="Test Standard", type="select"))
    position = Column(String(512), default="", info=dict(
        index=7, label="Location"
    ))
    env_temperature = Column(String(512), default="0", info=dict(
        index=11, label="Test Temperature"
    ))
    env_humidity = Column(String(512), default="", info=dict(
        index=10, label="Environment Temperature"
    ))
    real_peer_angle = Column(String(512), default="")
    comments = Column(String(512), default="")

    stripwidth = Column(String(512), default="10", info=dict(
        index=6, label="Strip Width"
    ))
    pressureThreshold = Column(String(512), default="")
    distance = Column(String(512), default="", info=dict(
        index=13, label="Peel Displacement"
    ))
    motorEnable = Column(String(512), default="")
    begint = Column(Integer)
    stopt = Column(Integer)
    endt = Column(Integer, default="", info=dict(
        index=14, label="Test Date"
    ))

    def __init__(self, loop_t=2*3600, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "<%s(id:%s;data:%s)>" % (self.__tablename__, self.id, len(self.data))

    @ staticmethod
    def formdump():
        rt = []
        for key, v in BljRecord.dump().items():
            v["key"] = key
            if v.get("index", None) != None:
                rt.append(v)
        return sorted(rt, key=lambda a: a["index"])


class BljHistoryData(Base):
    __tablename__ = "blj_history_data"
    pressure = Column(Float(10))
    temperature = Column(Float(10))
    record_id = Column(Integer, ForeignKey("blj_record.id"))
    p = relationship(BljRecord, backref="data")

    def __init__(self, pressure, temperature, t=None, **kwargs):
        self.pressure = pressure
        self.temperature = temperature
        self.t = t or time.time()
        super().__init__(**kwargs)

    def init(self):
        self.max_p = self.pressure
        self.min_p = self.pressure
        self.sum_p = self.pressure
        self.max_t = self.temperature
        self.min_t = self.temperature
        self.sum_t = self.temperature
        self.num = 1
    ts = "0-0[1]"

    def calc(self, v, ts):
        self.sum_p += v.pressure
        self.sum_t += v.temperature
        self.num += 1
        self.ts = "%.1f-%.1f[%s]" % (ts/60, (ts+v.t-self.t)/60, self.num)
        if v.pressure > self.max_p:
            self.max_p = v.pressure
        if v.pressure < self.min_p:
            self.min_p = v.pressure
        if v.temperature < self.min_t:
            self.min_t = v.temperature
        if v.temperature > self.max_t:
            self.max_t = v.temperature

    def array(self):
        return [self.ts] + ["%.1f" % d for d in [self.max_p, self.averge(self.sum_p), self.min_p, self.max_t, self.averge(self.sum_t), self.min_t]]

    def averge(self, p):
        if self.num == 0:
            return p
        else:
            return p/self.num


class BljConfig(Base):
    __tablename__ = "blj_config"
    value = Column(Text, default="")
    key = Column(String)

# class RecordTm(Base):
#     __tablename__ = "blj_record_tm"
#     begint = Column(Integer)
#     endt = Column(Integer)
#     mint_value = Column(Integer)
#     maxt_value = Column(Integer)
#     sumt_value = Column(Integer)
#     averaget_value = Column(Integer)
#     averagevalue = Column(Integer)
#     minvalue = Column(Integer)
#     maxvalue = Column(Integer)
#     sumvalue = Column(Integer)
#     record_id = Column(Integer)

#     def __init__(self, **kwargs):
#         self.minvalue = None
#         self.maxvalue = None
#         self.maxt_value = None
#         self.mint_value = None
#         self.averagevalue = None
#         self.averaget_value = None
#         self.sumt_value = 0
#         self.sumvalue = 0
#         self.begint = time.time()
#         self.endt = time.time()
#         # self.head = ""
#         super().__init__(**kwargs)

#     def append(self, speed, temp):
#         self.sumt_value += temp
#         self.sumvalue += speed
#         if self.maxvalue is None or speed > self.maxvalue:
#             self.maxvalue = speed
#         if self.minvalue is None or speed < self.minvalue:
#             self.minvalue = speed
#         if self.maxt_value is None or temp > self.maxt_value:
#             self.maxt_value = temp
#         if self.mint_value is None or temp < self.mint_value:
#             self.mint_value = temp
#         self.data.append(BljHistoryData(speed, temp, self))
#         self.averagevalue = self.average()
#         self.averaget_value = self.averaget()
#         self.endt = time.time()

#     @property
#     def head(self):
#         # print(self.begint, self.endt)
#         if self.begint is None or self.endt is None:
#             rt = ""
#         else:
#             rt = "%s->%s" % (function.now_str(self.begint, formats="%H:%M:%S"),
#                              function.now_str(self.endt, formats="%H:%M:%S"))
#         return rt

#     def average(self):
#         return self.sumvalue/len(self.data) if len(self.data) else 0

#     def averaget(self):
#         return self.sumt_value/len(self.data) if len(self.data) else 0

#     def stop(self):
#         self.endt = time.time()


if __name__ == "__main__":
    pass
