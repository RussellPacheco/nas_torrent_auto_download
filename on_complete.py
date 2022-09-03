import os, json, sys, configparser, signal

config = configparser.ConfigParser()
config.read("config.ini")

with open("running_ps.json", "w+") as file:
    data = json.load(file)
    dpid_pid_pairs = data["running_ps"].split(";")
    to_delete = None
    for id_pair in dpid_pid_pairs:
        ident = id_pair.split(":")
        if sys.argv[1] in ident:
            try:
                os.kill(int(ident[1]), signal.SIGSTOP)
            except PermissionError:
                pass
            try: 
                os.rmdir(os.path.join(config["DEFAULT"]["WATCH_FOLDER"], ident[2]))
            except FileNotFoundError:
                pass
            to_delete = id_pair
    dpid_pid_pairs.remove(to_delete)
    data["running_ps"] = ";".join(dpid_pid_pairs)
    file.write(json.dump(data))

