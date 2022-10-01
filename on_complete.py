import os, json, sys, signal, shutil

signal.SIGBREAK

data = None
dp_uuid = sys.argv[1]
with open("running_ps.json", "r") as file:
    data = json.load(file)

dpid_pid_pairs = data["running_ps"].split(";")
to_delete = None
for id_pair in dpid_pid_pairs:
    ident = id_pair.split(":")
    if dp_uuid in ident:
        try:
            print(f"Killing download process for {ident[2]}")
            if sys.platform == "win32":
                os.kill(int(ident[1]), signal.SIGBREAK)
            else:
                os.kill(int(ident[1]), signal.SIGSTOP)
        except PermissionError:
            pass
        try: 
            shutil.rmtree(os.path.join(data["watch_folder"], ident[2]))
            shutil.rmtree(os.path.join(data["watch_folder"], f"{ident[0]}.log"))
        except FileNotFoundError:
            pass
        to_delete = id_pair
dpid_pid_pairs.remove(to_delete)
data["running_ps"] = ";".join(dpid_pid_pairs)

with open("running_ps.json", "w") as file:
    file.write(json.dumps(data))

