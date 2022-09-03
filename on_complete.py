import os, json, sys

with open("running_ps.json", "w+") as file:
    data = json.load(file)
    dpid_pid_pairs = data["running_ps"].split(";")
    to_delete = None
    for id_pair in dpid_pid_pairs:
        ident = id_pair.split(":")
        if sys.argv[1] in ident:
            os.kill(ident[1])
            to_delete = id_pair
    dpid_pid_pairs.remove(to_delete)
    data["running_ps"] = ";".join(dpid_pid_pairs)
    file.write(json.dump(data))

