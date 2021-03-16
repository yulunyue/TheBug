import _thread
from common.build import Program
import os
from common.filehandel import FileWatch
from common.websocket_server import run_thread
web_socket = run_thread(50000)


def util(*args):
    web_socket.send("watchfile", dict(src_path="js/dist/index/main.js"))


p = Program("./js/src/index.js", on_finish=util)
_thread.start_new_thread(p.run, ())

# def system(s):
#     print(s)
#     return os.system(s)


# def compile_js(src):
#     src = src.replace("js/", "")

#     dst = src.replace('src/', 'dist/').replace(".js", "")
#     os.chdir("js")
#     system("webpack build --mode=development ./%s -o %s" % (src, dst))
#     os.chdir("../")


# def js_file_change(e):
#     if "src/" in e["src_path"]:
#         compile_js(e["src_path"])
#     elif "dst/" in e["src_path"]:
#         web_socket.send("filewatch", e)


# FileWatch("js").on_file_change(js_file_change)


def js(env, *args, **kwargs):
    rt = ""
    path = env.path[1:]
    if os.path.exists(path):
        with open(path, "rb") as f:
            rt = f.read()
    else:
        rt = path
    return rt
