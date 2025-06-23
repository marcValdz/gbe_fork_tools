import os
import sys
import json
import shutil
import subprocess
import time

# Try to import psutil at the top
try:
    import psutil
except ImportError:
    psutil = None

# Constants
SRC_DIR = os.path.join('.', 'output')
AW_PATH = os.path.join(os.environ.get('APPDATA', ''), 'Achievement Watcher')
AW_WATCHDOG_DIR = r"C:\Program Files\Achievement Watcher\nw"
SCHEMA_REL_PATH = os.path.join('Achievement Watcher', 'steam_cache', 'schema')
AW_SCHEMA_DEST = os.path.join(AW_PATH, 'steam_cache', 'schema')
AW_CFG_DEST = os.path.join(AW_PATH, 'cfg')


def aggregate_game_indexes(src):
    """Aggregate all gameIndex.json files into a single list."""
    game_list = []
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            schema_path = os.path.join(item_path, SCHEMA_REL_PATH)
            if os.path.exists(schema_path):
                json_path = os.path.join(schema_path, "gameIndex.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                game_list.extend(data)
                            else:
                                game_list.append(data)
                    except Exception as e:
                        print(f"Error parsing JSON file {json_path}: {e}")
                        continue
    return game_list

def merge_schema_files(src, dest):
    """Merge all schema files from all games into the destination directory."""
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            schema_path = os.path.join(item_path, SCHEMA_REL_PATH)
            if os.path.exists(schema_path):
                for entry in os.scandir(schema_path):
                    if entry.name.lower() == "gameindex.json":
                        continue
                    src_item = entry.path
                    dest_item = os.path.join(dest, entry.name)
                    if entry.is_dir():
                        os.makedirs(dest_item, exist_ok=True)
                        for file_entry in os.scandir(src_item):
                            if file_entry.is_file():
                                shutil.copy2(file_entry.path, os.path.join(dest_item, file_entry.name))
                    else:
                        shutil.copy2(src_item, dest_item)

def export_game_index(sorted_list, schema_index_path, cfg_index_path):
    sorted_json = json.dumps(sorted_list, indent=4)
    with open(schema_index_path, "w", encoding="utf-8") as f:
        f.write(sorted_json)
    with open(cfg_index_path, "w", encoding="utf-8") as f:
        f.write(sorted_json)

def stop_aw_watchdog():
    print("Stopping AW Watchdog (node.exe)...")
    if psutil:
        found = False
        for proc in psutil.process_iter(attrs=["name"]):
            pname = proc.info["name"] or ""
            if pname.lower() in ["node.exe", "node"]:
                proc.kill()
                found = True
        if found:
            print("Successfully stopped AW Watchdog.")
        else:
            print("Error: node.exe is not running.")
    else:
        try:
            subprocess.run(["taskkill", "/IM", "node.exe", "/F"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Successfully stopped AW Watchdog.")
        except subprocess.CalledProcessError:
            print("Error: node.exe is not running or could not be stopped.")

def start_aw_watchdog(wd):
    print("Restarting AW Watchdog (node.exe)...")
    exe = os.path.join(wd, "nw.exe")
    if os.path.exists(exe):
        try:
            subprocess.Popen([exe, "-config", "watchdog.json"], cwd=wd)
            print("Successfully restarted AW Watchdog.")
        except Exception as e:
            print(f"Error: Failed to start AW Watchdog: {e}")
    else:
        print(f"Error: '{exe}' does not exist. AW Watchdog executable is missing.")

def main():
    if not os.path.exists(SRC_DIR):
        print(r".\output directory doesn't exist. Please run `generate_emu_config.exe` first.")
        sys.exit(1)

    if not os.path.exists(AW_PATH):
        os.makedirs(AW_PATH, exist_ok=True)
    os.makedirs(AW_SCHEMA_DEST, exist_ok=True)
    os.makedirs(AW_CFG_DEST, exist_ok=True)

    # Aggregate gameIndex.json files
    game_list = aggregate_game_indexes(SRC_DIR)

    # Merge schema files
    merge_schema_files(SRC_DIR, AW_SCHEMA_DEST)

    # Sort and export gameIndex.json
    sorted_list = sorted(game_list, key=lambda x: x.get("appid", 0), reverse=True)
    schema_index_path = os.path.join(AW_SCHEMA_DEST, "gameIndex.json")
    cfg_index_path = os.path.join(AW_CFG_DEST, "gameIndex.json")
    export_game_index(sorted_list, schema_index_path, cfg_index_path)

    # Restart AW Watchdog
    if not os.path.exists(AW_WATCHDOG_DIR):
        print(f"Error: Achievement Watcher is not installed. Directory '{AW_WATCHDOG_DIR}' does not exist.")
        sys.exit(1)

    stop_aw_watchdog()
    time.sleep(2)
    start_aw_watchdog(AW_WATCHDOG_DIR)

    print("Achievement Watcher updated successfully!")

if __name__ == "__main__":
    main()
