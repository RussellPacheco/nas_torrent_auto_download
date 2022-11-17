#!/usr/bin/env python3

import os, json, sys, signal, shutil, subprocess


data = None
pid = None
project_root = None
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

with open(data_file, "r") as file:
    data = json.load(file)
    pid = data["pid"]
try:
    print(f"\nKilling process: {pid}")
    if sys.platform == "win32":
        os.kill(int(pid), signal.SIGBREAK)
    else:
        os.kill(int(pid), signal.SIGKILL)
except PermissionError:
    pass

on_kill_file = os.path.join(data["project_root"], "on_kill.py")
subprocess.Popen(["python3", f"{on_kill_file}", str(pid)], start_new_session=True)

