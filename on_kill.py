import shutil, os, json, sys


PID_to_kill = sys.argv[1]

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(PROJECT_ROOT, "running_ps.json")
with open(json_file, "r") as file:
    data = json.load(file)

ID_list = data["running_ps"].split(";")

for ID_pair in ID_list:
    PID_dirname = ID_pair.split(":")
    if PID_to_kill in PID_dirname:
        try: 
            shutil.rmtree(os.path.join(data["watch_folder"], PID_dirname[1]))
            os.remove(os.path.join(PROJECT_ROOT, f"{PID_to_kill}.log"))
        except FileNotFoundError:
            pass
        to_delete = ID_pair
ID_list.remove(to_delete)
data["running_ps"] = ";".join(ID_list)

with open(json_file, "w") as file:
    file.write(json.dumps(data))