import os, subprocess, json, argparse, shutil, stat
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


parser = argparse.ArgumentParser(prog="Nas Torrent Auto Downloader", description="Automatically watches specified download folders for torrent files, and if found, downloads torrent.")
parser.add_argument("-w", "--watch-path", required=True, help="Set the folder to watch")
parser.add_argument("-d", "--download-folder", required=True, help="Set the download folder")
args = parser.parse_args()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
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

        if torrent_file.endswith('.torrent'):
            if parent != watch_folder_parent and parent_parent == watch_folder_parent:
                print(f"""
New file detected!
    - Filename: {torrent_file}
    - Parent_dir: {parent}       
                """)
                new_folder_path = os.path.join(download_folder, parent)
                self._create_folder(new_folder_path=new_folder_path)
                download_ps = self._run_torrent_downloader(torrent_file_abspath=torrent_file_abspath, new_folder_path=new_folder_path, watch_folder_parent_path=parent_dir)
                #download_ps = self._run_test_process(dp_uuid=dp_uuid)
                self._copy_on_complete_files(parent_dir=parent_dir, pid=download_ps.pid)
                self._update_json(download_pid=download_ps.pid, parent=parent)
       
    def _create_folder(self, new_folder_path: str):
        try:
            os.mkdir(new_folder_path)
            print(f"File folder is created at {new_folder_path}")
        except FileExistsError:
            pass
        return new_folder_path

    def _copy_on_complete_files(self, parent_dir, pid):
        data_file = os.path.join(parent_dir, "data")
        with open(data_file, "w") as file:
            data = {
                "pid": pid,
                "project_root": PROJECT_ROOT
            }
            json.dump(data, file)       
        on_complete_file = os.path.join(PROJECT_ROOT, "on_complete.py")
        copied_complete_file = os.path.join(parent_dir, "on_complete.py")
        shutil.copyfile(on_complete_file, copied_complete_file)
        os.chmod(copied_complete_file, stat.S_IRWXU)

    def _run_test_process(self):
        download_ps = subprocess.Popen(["python", "ongoing_process.py"])
        print(f"Test process is being run at PID: {download_ps.pid}")
        return download_ps

    def _run_torrent_downloader(self, torrent_file_abspath: str, new_folder_path: str, watch_folder_parent_path: str):
        #devnull = open(os.devnull, "wb")
        on_complete_file_abspath = os.path.join(watch_folder_parent_path, "on_complete.py")
        download_ps = subprocess.Popen(["aria2c", "-T", torrent_file_abspath, "-d", new_folder_path, "--file-allocation=falloc", "-V", "true", f'--on-bt-download-complete={on_complete_file_abspath}', "--show-console-readout=false"], start_new_session=True)
        print(f"Aria is being run at PID: {download_ps.pid}")
        return download_ps
    
    def _update_json(self, download_pid: str, parent: str):
        with open("running_ps.json", "w+") as file:
            data = None
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {} 

            data["watch_folder"] = watch_path

            if "running_ps" not in data:
                data["running_ps"] = f"{download_pid}:{parent}"
            else:
                data["running_ps"] = f"{data['running_ps']};{download_pid}:{parent}"

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



