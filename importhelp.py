import os
import shutil
from tkinter import filedialog
import subprocess
import sys
import time
import_folder = filedialog.askdirectory(title="Select Folder to Import From")

if not import_folder:
   print("Import cancelled.")
   sys.exit(1)
def wait_for_file_free(filepath, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(filepath, "a"):
                return True
        except PermissionError:
            print(f"File '{filepath}' is busy... retrying.")
        time.sleep(1)
    print("Timeout waiting for file to be free.")
    sys.exit(1)
def is_folder_free(folder_path, timeout=120):
    start_time = time.time()
    test_name = folder_path + "_testcheck"
    while time.time() - start_time < timeout:
        try:
            # Try renaming folder
            os.rename(folder_path, test_name)
            os.rename(test_name, folder_path)
            print(start_time)
            return True  # Folder is free
        except PermissionError:
            time.sleep(1)  # Wait and retry
        except FileNotFoundError:
            print("Folder not found.")
            sys.exit(1)
    print("Timeout waiting for folder to be free.")
    sys.exit(1)
wait_for_file_free("chatbot_memory.db", timeout=10)
is_folder_free("db", timeout=10)
src_db_file = os.path.join(import_folder, "chatbot_memory.db")
if os.path.exists(src_db_file):
    shutil.copy2(src_db_file, "chatbot_memory.db")
else:
    sys.exit(1)
src_db_folder = os.path.join(import_folder, "db")
if os.path.exists(src_db_folder):
    if os.path.exists("db"):
        shutil.rmtree("db")
    shutil.copytree(src_db_folder, "db")
else:
    sys.exit(1)
main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "type2.py"))
subprocess.Popen([sys.executable, main_path])
print("Import completed successfully.")

sys.exit(0)
