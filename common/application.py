from . import function
import re

class UtilClassCall:
    def __init__(self, oj, name):
        self._oj = oj
        self.name = name

    def call(self, *args, **kwargs):
        return getattr(self._oj, self.name)(*args, **kwargs)


class Application:
    def __init__(self, _map):
        self._map = _map
        self._map_dict = dict()
        self._re_array=[]
        self.updateMap()

    def updateMap(self):
        for key in self._map:
            p = self.parse(key[0], key[1])
            if key[0] in self._map_dict:
                raise Exception("can not register twise",
                                key[0], self._map_dict[key])
            if p:
                self._map_dict[key[0]] = p

    def parse(self, k, v):
        if type(v).__name__ == 'type':
            v1 = v()
            for key in function.dirs(v1, lambda c: callable(c)).keys():
                self._map_dict[k+'/'+key
                               ] = UtilClassCall(v1, key)
        elif ".*" in k:
            self._re_array.append([re.compile(k),v])
            return
        return v

    def call(self, name, *args, **kwargs):
    
        call = self._map_dict[name]
        if isinstance(call, UtilClassCall):
            return call.call(*args, **kwargs)
        return call(*args, **kwargs)

    def __repr__(self):
        return "Application:"+",".join(self._map_dict.keys())
