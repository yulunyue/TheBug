import time
import os
import json
import sys


def listdir(p, index=0, filter=None):
    rt = [p+'/'+d for d in os.listdir(p)]
    if index >= 0:
        pass
    if filter:
        rt = [filter(d) for d in rt if filter(d)]
    return rt


def aim(p, dst):
    return p.replace('/', '_').replace('.cpp', '').replace('.c', '')+dst


def shell(s, *args, chdir=None):
    d = s % (args)
    print(d)
    if chdir:
        os.chdir(chdir)
    a = os.system(d)

    if a != 0:
        exit()


class Db():
    def __init__(self, p):
        if os.path.exists(p):
            f = open(p, 'r')
            try:
                data = json.loads(f.read())
                f.close()
                self.files = data["files"]
                self.relations = data["relations"]
            except:
                self.files = {}
                self.relations = {}
        else:
            self.files = {}
            self.relations = {}
        self._path = p

    def update(self):
        with open(self._path, "w") as f:
            f.write(json.dumps(
                dict(files=self.files, relations=self.relations), indent=4))
            f.flush()

    def hasupdate(self, src, dst):
        rt = False
        if isinstance(src, str):
            src = [src]
        srch = [d.replace(".cpp", '.h').replace('.c', '.h')
                for d in src if '.cpp' in d or '.c' in d]
        src += srch
        for s in src:
            tm = int(os.path.getmtime(s))
            if self.files.get(s, None) != tm:
                self.files[s] = tm
                rt = True
            self.files[s] = tm
        self.relations[dst] = src
        return rt


db = Db("temp/db.json")


class MyFile():
    def __init__(self, p):
        self._path = p

    def files(self):
        if isinstance(self._path, list):
            return [self._path[0]+'/'+d for d in self._path[1:]]
        if os.path.isfile(self._path):
            return [self._path]
        else:
            return self.fileany(self._path.split('/'))

    def fileany(self, p):
        if p[-1] == "*":
            p2 = "/".join(p[:-1])
            return listdir(p2)+[p2]
        else:
            return ["/".join(p)]


class MyFiles:
    def __init__(self, p):
        self._map = lambda v: v
        self._path = [MyFile(d) for d in p]

    def files(self):
        rt = []
        for d in self._path:
            rt += d.files()
        return [self._map(d) for d in rt if self._map(d)]

    def pre(self, v, extend=[]):
        p = self.files()+extend
        return [v+d for d in p]

    def map(self, v):
        self._map = v
        return self


class Base():
    args = ["-g", "-Wfatal-errors"]
    dst_dir = "build"
    cc = "g++"
    inc_path: MyFiles = MyFiles([])
    lib_path: MyFiles = MyFiles([])
    libs = MyFiles([])
    src_path = "main.cpp"
    pre_build = []
    chdir = ""

    def __init__(self, p, on_finish=None):
        self.on_finish = on_finish
        if isinstance(p, str):
            if p[-3:] == '.js':
                self.src_path = p
                self.cc = "webpack"
            else:
                if os.path.exists(p):
                    for key, v in json.loads(open(p, "r").read()).items():
                        if key in ["inc_path", "lib_path", "libs"]:
                            setattr(self, key, MyFiles(v))
                        else:
                            setattr(self, key, v)
                else:
                    with open(p, "w") as f:
                        f.write(json.dumps(
                            dict(
                                src_path=self.src_path,
                                pre_build=self.pre_build,
                                inc_path=[],
                                lib_path=[],
                                libs=[],
                                chdir=self.chdir,
                                dst_dir=self.dst_dir,
                                cc=self.cc
                            ),
                            indent=4))
                if not os.path.exists(self.dst_dir):
                    os.mkdir(self.dst_dir)
        else:
            self.inc_path = p.inc_path
            self.lib_path = p.lib_path
            self.args = p.args
            self.libs = p.libs

    def shell(self, *args):
        rt = []
        for d in args:
            if isinstance(d, list):
                rt += d
            else:
                rt.append(d)
        try:
            shell(" ".join(rt), chdir=self.chdir)
        except Exception as e:
            print(rt, e)
            exit()

    def run2(self):
        return ''

    def run(self):
        rt = self.run2()
        db.update()
        return rt


class Oj(Base):
    def __init__(self, src, p):
        super().__init__(p)
        self.src_path = src
        self.dst = self.dst_dir+'/'+aim(src, ".o")

    def run2(self):
        # print("make", self.dst)
        if db.hasupdate(self.src_path, self.dst):
            self.shell(
                self.cc,
                self.args,
                "-I. -I..",
                self.inc_path.pre("-I"),
                self.lib_path.pre("-L"),
                "-c",
                self.src_path,
                "-o",
                self.dst
            )
        return self.dst


class Lib(Base):
    def __init__(self, p, p2):
        super().__init__(p2)
        self.dst = self.dst_dir+'/'+aim(p, '.dll')
        self.src_path = [Oj(d, self) for d in listdir(p, filter=self.filter)]

    def filter(self, v):
        if v.split(".").pop() in ["c", "cpp"]:
            return v

    def run2(self):
        src_path = [d.run() for d in self.src_path]
        if db.hasupdate(src_path, self.dst):
            self.shell(
                self.cc,
                self.args+["-shared"],
                "-I. -I..",
                self.inc_path.pre("-I"),
                self.lib_path.pre("-L"),
                self.libs.pre("-l"),
                src_path,
                "-o",
                self.dst
            )
        return self.dst

    def path(self):
        return self.dst


class Program(Base):
    libs_make = []

    def run2(self):
        pre_build = [Lib(d, self).run() for d in self.pre_build]
        if self.cc == "webpack":
            return self.run_js()
        dst = self.dst_dir+'/'+aim(self.src_path, ".exe")
        if db.hasupdate([self.src_path]+pre_build, dst):
            self.shell(
                self.cc,
                self.args,
                "-I. -I.. -Lbuild",
                self.inc_path.pre("-I"),
                self.lib_path.pre("-L"),
                self.libs.pre("-l", extend=[aim(d, "")
                                            for d in self.pre_build]),
                self.src_path,
                "-o",
                dst
            )

    def run_js(self):
        dst = self.src_path.replace('src', 'dist').replace(".js", "")
        watch_paths = []

        def pack():
            # os.chdir(self.chdir)
            s1 = "webpack build --mode=development %s -o %s" % (
                self.src_path, dst)
            bt = time.time()
            flag = False
            a2 = os.popen(s1).read()
            for d in a2.split("\n"):
                d2 = d.split(" ")
                if d2[0] == "cacheable":
                    flag = True
                elif d2[0] == "webpack":
                    flag = False
                elif flag:
                    try:
                        c = d2[2][4:-10]
                        if c not in watch_paths:
                            watch_paths.append(c)
                    except:
                        print(a2)
                        return
                    # print(c)
            print("shell", s1, watch_paths, int((time.time()-bt)*10))
            if self.on_finish:
                self.on_finish()
        dt = dict()
        while True:
            if len(watch_paths) == 0:
                pack()
            for d in watch_paths:
                pm = int(os.path.getmtime(d))
                if d in dt and dt[d] != pm:
                    pack()
                    dt[d] = pm
                    break
                dt[d] = pm
            time.sleep(0.01)

class Pack:
    def __init__(self):
        


if __name__ == "__main__":
    Program(sys.argv[1]).run()
