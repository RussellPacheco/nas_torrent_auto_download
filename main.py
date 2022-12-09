import os, subprocess, json, argparse, shutil, stat, datetime, logging, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from torrent_process import handle_torrent_download


parser = argparse.ArgumentParser(prog="Nas Torrent Auto Downloader", description="Automatically watches specified download folders for torrent files, and if found, downloads torrent.")
parser.add_argument("-w", "--watch-path", required=True, help="Set the folder to watch")
parser.add_argument("-d", "--download-folder", required=True, help="Set the download folder")
parser.add_argument("-l", "--log-file", required=True, help="Specify the log file path.")
parser.add_argument("--log-level", required=False, help="DEBUG, INFO, WARNING, ERROR, CRITICAL", default="INFO")

args = parser.parse_args()

log_file = args.log_file
log_level = args.log_level

numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % log_level)

logging.basicConfig(filename=log_file, encoding="utf-8", level=log_level, format="[%(asctime)s] %(message)s")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
watch_path = os.path.normpath(args.watch_path)
download_folder = os.path.normpath(args.download_folder)

class Callback(FileSystemEventHandler):
    def on_any_event(self, event):
        pass

    def on_created(self, event):
        time.sleep(2)
        created_file_abspath = event.key[1]
        parent_folder = os.path.dirname(created_file_abspath)
        created_file = os.path.basename(event.key[1])
        if created_file.endswith(".torrent"):
            parent_dir = os.path.abspath(os.path.join(event.src_path, os.pardir))
            dir_files = os.listdir(parent_dir)
            if f"{created_file}_predownload" not in dir_files:
                try:
                    with open(f"{created_file_abspath}_predownload", "w") as file:
                        file.write("initial_download")
                except PermissionError:
                    os.chmod(path=parent_folder, mode=int("770", base=8))
                    with open(f"{created_file_abspath}_predownload", "w") as file:
                        file.write("initial_download")
                    pass
            else:
                self.on_new_file(event)

    def on_moved(self, event):
        self.on_new_file(event)
        
    def on_new_file(self, event):
        parent_dir = None
        if event.event_type == "created":
            parent_dir = os.path.abspath(os.path.join(event.src_path, os.pardir))
            torrent_file_abspath = event.key[1]
        if event.event_type == "moved":
            parent_dir = os.path.abspath(os.path.join(event.dest_path, os.pardir))
            torrent_file_abspath = event.key[2]
        parent = os.path.split(parent_dir)[1]
        parent_parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
        parent_parent = os.path.split(parent_parent_dir)[1]
        watch_folder_parent = os.path.split(watch_path)[1]
        torrent_file = os.path.basename(event.key[1])
        new_folder_path = os.path.join(download_folder, parent)

        if torrent_file.endswith('.torrent'):
            if parent != watch_folder_parent and parent_parent == watch_folder_parent:
                logging.info(f"New file detected:: Filename: {torrent_file} Filepath: {torrent_file_abspath} Parent_dir: {parent}")
                print(f"[{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}] New file detected:: Filename: {torrent_file} Filepath: {torrent_file_abspath} Parent_dir: {parent}")
                torrent_task_details = {
                    "new_folder_path": new_folder_path,
                    "torrent_file_abspath": torrent_file_abspath,
                    "watch_folder_parent_path": parent_dir,
                    "parent_dir": parent_dir,
                    "parent": parent,
                    "watch_path": watch_path,
                    "log_file": log_file,
                    "log_level": log_level
                }
                handle_torrent_download.delay(torrent_task_details)
        


observer = Observer()
callback = Callback()

path = watch_path

observer.schedule(event_handler=callback, path=path, recursive=True)
logging.info(f"Watch Dog is running")
print(f"[{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}] Watch Dog is running")
observer.start()


try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()



