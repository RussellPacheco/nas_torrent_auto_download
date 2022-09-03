import os, configparser, subprocess, json, uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config = configparser.ConfigParser()
config.read("config.ini")


class Callback(FileSystemEventHandler):
    def on_created(self, event):
        parent_dir = os.path.abspath(os.path.join(event.src_path, os.pardir))
        parent = os.path.split(parent_dir)[1]
        parent_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
        parent_parent = os.path.split(parent_parent_dir)[1]
        watch_folder_parent = os.path.split(config["DEFAULT"]["WATCH_FOLDER"])[1]
        torrent_file = os.path.basename(event.key[1])

        if not event.is_directory and torrent_file.endswith('.torrent'):
            if parent != watch_folder_parent and parent_parent == watch_folder_parent:
                new_folder_path = os.path.join(config["DEFAULT"]["DOWNLOAD_FOLDER"], parent)
                try:
                    os.mkdir(new_folder_path)
                except FileExistsError:
                    pass
                dpid = str(uuid.uuid4())
                download_ps = subprocess.Popen(["aria2c", "-T", torrent_file, "-d", new_folder_path, "--file-allocation=falloc", "-V", "true", f'--on-bt-download-complete="python on_complete.py {dpid}"'])
                data = None
                with open("running_ps.json", "w+") as file:
                    data = None
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}

                    if "running_ps" not in data:
                        data["running_ps"] = dpid + ":" + download_ps.pid + ":" + parent
                    else:
                        data["running_ps"] = data["running_ps"] + ";" + dpid + ":" + download_ps

                    file.write(json.dumps(data))



observer = Observer()
callback = Callback()

path = config["DEFAULT"]["WATCH_FOLDER"]

observer.schedule(event_handler=callback, path=path, recursive=True)
print("Watch Dog is running")
observer.start()


try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()



