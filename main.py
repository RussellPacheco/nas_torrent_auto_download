import os, subprocess, json, uuid, argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


parser = argparse.ArgumentParser(prog="Nas Torrent Auto Downloader", description="Automatically watches specified download folders for torrent files, and if found, downloads torrent.")
parser.add_argument("-w", "--watch-path", required=True, help="Set the folder to watch")
parser.add_argument("-d", "--download-folder", required=True, help="Set the download folder")
args = parser.parse_args()

watch_path = os.path.normpath(args.watch_path)
download_folder = os.path.normpath(args.download_folder)

class Callback(FileSystemEventHandler):
    def on_created(self, event):
        parent_dir = os.path.abspath(os.path.join(event.src_path, os.pardir))
        parent = os.path.split(parent_dir)[1]
        parent_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
        parent_parent = os.path.split(parent_parent_dir)[1]
        watch_folder_parent = os.path.split(watch_path)[1]
        torrent_file = os.path.basename(event.key[1])
        torrent_file_abspath = event.key[1]
        dp_uuid = str(uuid.uuid4())

        if torrent_file.endswith('.torrent'):
            if parent != watch_folder_parent and parent_parent == watch_folder_parent:
                print(f"""
New file detected!
    - Filename: {torrent_file}
    - Filepath: {torrent_file_abspath}
    - Parent_dir: {parent}       
                """)
                new_folder_path = os.path.join(download_folder, parent)
                self._create_folder(new_folder_path=new_folder_path)
                download_ps = self._run_torrent_downloader(dp_uuid=dp_uuid, torrent_file_abspath=torrent_file_abspath, new_folder_path=new_folder_path)
                #download_ps = self._run_test_process(dp_uuid=dp_uuid)
                self._update_json(dp_uuid=dp_uuid, download_ps=download_ps.pid, parent=parent)
        

    def _create_folder(self, new_folder_path: str):
        try:
            os.mkdir(new_folder_path)
            print(f"File folder is created at {new_folder_path}")
        except FileExistsError:
            pass
        return new_folder_path

    def _run_test_process(self, dp_uuid: str):
        download_ps = subprocess.Popen(["python", "ongoing_process.py", f"{dp_uuid}"])
        print(f"Test process is being run at PID: {download_ps.pid}")
        return download_ps

    def _run_torrent_downloader(self, dp_uuid: str, torrent_file_abspath: str, new_folder_path: str):
        #devnull = open(os.devnull, "wb")
        download_ps = subprocess.Popen(["aria2c", "-T", torrent_file_abspath, "-d", new_folder_path, "--file-allocation=falloc", "-V", "true", f'--on-bt-download-complete="python3 on_complete.py {dp_uuid}"', "--show-console-readout=false", "--log-level=notice", f"--log={dp_uuid}.log"])
        print(f"Aria is being run at PID: {download_ps.pid}")
        return download_ps
    
    def _update_json(self, dp_uuid: str, download_ps: str, parent: str):
        with open("running_ps.json", "w+") as file:
            data = None
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {} 

            data["watch_folder"] = watch_path

            if "running_ps" not in data:
                data["running_ps"] = f"{dp_uuid}:{download_ps}:{parent}"
            else:
                data["running_ps"] = f"{data['running_ps']};{dp_uuid}:{download_ps}"

            file.write(json.dumps(data))

observer = Observer()
callback = Callback()

path = watch_path

observer.schedule(event_handler=callback, path=path, recursive=True)
print("Watch Dog is running")
observer.start()


try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()



