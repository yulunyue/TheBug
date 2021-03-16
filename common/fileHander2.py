import json
import os
from typing import List


class FileBak:
    def __init__(self, path, p):
        self._path = path
        self._p = p

    def check(self):
        if self._path in self._p._db:
            return
        if self._path[-4:] != ".bak" and not os.path.exists(self._path+".bak"):
            os.rename(self._path, self._path+".bak")
            v = self._p.check()
            if v != 0:
                if os.path.isfile(self._path):
                    self._p._db.append(self._path)
                os.rename(self._path+".bak", self._path)
            if os.path.isdir(self._path):
                for d in os.listdir(self._path):
                    FileBak(self._path+'/'+d, self._p).check()

            print("check", v, self._path)

    def repair(self):
        if self._path[-4:] == ".bak":
            p = self._path[:-4]
            # print(self._path, p)
            if not os.path.exists(p):
                print("repair", self._path, p)
                os.rename(self._path, p)
        else:
            p = self._path
        if os.path.isdir(p):
            for d in os.listdir(p):
                FileBak(p+'/'+d, self._p).repair()


class SheelRun:
    def __init__(self, p):
        self._path = p
        self._db = json.loads(open("temp/db.json", "r").read())
        self._f = open("temp/db.json", "w")
        self._files_depends: List[FileBak] = []
        os.chdir(self._path)
        for d in os.listdir(p):
            self._files_depends.append(FileBak(self._path+'/'+d, self))

    def check(self):
        return os.system("blj.exe blj.py")

    def run(self):
        try:
            if self.check() != 0:
                # print("checkerror please repair")
                # for d in self._files_depends:
                #     d.repair()
                # FileBak("./", self).repair()
                raise "checkerror please repair"
            else:
                for d in self._files_depends:
                    d.check()
        except Exception as e:
            print("errroe", e)
        self.check()
        self._f.write(json.dumps(self._db, indent=4))
        self._f.close()


if __name__ == "__main__":
    SheelRun("D:/project/blj/dist").run()
