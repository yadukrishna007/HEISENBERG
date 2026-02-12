import subprocess
import os

def open_app(app_path: str):
    subprocess.Popen(app_path)

def open_folder(folder: str):
    os.startfile(folder)