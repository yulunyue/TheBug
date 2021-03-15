from common.httpsimple import run, HttpApplication, run_thread
from js.app import js
run_thread(80, HttpApplication([
    ["/(.*)", js]
]))
input("exit")
