import os
import sys
import json
import shutil
import psutil
import subprocess
import time


# Constants
SRC_DIR = os.path.join(".", "output")

AW_PATH = os.path.join(os.environ.get("APPDATA", ""), "Achievement Watcher")
SCHEMA_REL_PATH = os.path.join("Achievement Watcher", "steam_cache", "schema")

AW_SCHEMA_DEST = os.path.join(AW_PATH, "steam_cache", "schema")
AW_CFG_DEST = os.path.join(AW_PATH, "cfg")

PROGRAM_FILES = os.environ.get("ProgramFiles", r"C:\Program Files")
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", "")

AW_WATCHDOG_CANDIDATES = [
    os.path.join(PROGRAM_FILES, "Achievement Watcher", "nw"),
    os.path.join(LOCAL_APPDATA, "Programs", "Achievement Watcher", "nw"),
]


def find_aw_watchdog_dir(candidates):
    for path in candidates:
        exe = os.path.join(path, "nw.exe")
        if os.path.exists(exe):
            return path
    return None


def scan_source(src):
    """
    Single-pass scan of SRC_DIR to reduce redundant filesystem traversal.
    Returns:
        game_json_paths: list[str]
        schema_dirs: list[str]
    """
    game_json_paths = []
    schema_dirs = []

    for entry in os.scandir(src):
        if not entry.is_dir():
            continue

        schema_path = os.path.join(entry.path, SCHEMA_REL_PATH)

        if not os.path.isdir(schema_path):
            continue

        schema_dirs.append(schema_path)

        json_path = os.path.join(schema_path, "gameIndex.json")
        if os.path.exists(json_path):
            game_json_paths.append(json_path)

    return game_json_paths, schema_dirs


def aggregate_game_indexes(json_paths):
    game_list = []

    for path in json_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                game_list.extend(data)
            else:
                game_list.append(data)

        except Exception as e:
            print(f"Error parsing JSON file {path}: {e}")

    return game_list


def merge_schema_files(schema_dirs, dest):
    os.makedirs(dest, exist_ok=True)

    for schema_path in schema_dirs:
        for entry in os.scandir(schema_path):
            if entry.name.lower() == "gameindex.json":
                continue

            dest_item = os.path.join(dest, entry.name)

            if entry.is_dir():
                shutil.copytree(entry.path, dest_item, dirs_exist_ok=True)
            else:
                shutil.copy2(entry.path, dest_item)


def export_game_index(sorted_list, schema_index_path, cfg_index_path):
    data = json.dumps(sorted_list, indent=4)

    with open(schema_index_path, "w", encoding="utf-8") as f:
        f.write(data)

    with open(cfg_index_path, "w", encoding="utf-8") as f:
        f.write(data)


def stop_aw_watchdog():
    print("Stopping AW Watchdog (node.exe)...")

    found = False

    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            name = proc.info["name"]
            if name and name.lower() == "node.exe":
                proc.kill()
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if found:
        print("Successfully stopped AW Watchdog.")
    else:
        print("Warning: node.exe was not running.")


def start_aw_watchdog(wd):
    print("Restarting AW Watchdog (node.exe)...")

    exe = os.path.join(wd, "nw.exe")

    if not os.path.exists(exe):
        print(f"Error: '{exe}' does not exist.")
        return

    subprocess.Popen([exe, "-config", "watchdog.json"], cwd=wd)
    print("Successfully restarted AW Watchdog.")


def main():
    if not os.path.exists(SRC_DIR):
        print(r".\output directory doesn't exist. Please run `generate_emu_config.exe` first.")
        sys.exit(1)

    os.makedirs(AW_SCHEMA_DEST, exist_ok=True)
    os.makedirs(AW_CFG_DEST, exist_ok=True)

    json_paths, schema_dirs = scan_source(SRC_DIR)
    game_list = aggregate_game_indexes(json_paths)
    merge_schema_files(schema_dirs, AW_SCHEMA_DEST)
    sorted_list = sorted(game_list, key=lambda x: x.get("appid", 0), reverse=True)

    schema_index_path = os.path.join(AW_SCHEMA_DEST, "gameIndex.json")
    cfg_index_path = os.path.join(AW_CFG_DEST, "gameIndex.json")
    export_game_index(sorted_list, schema_index_path, cfg_index_path)

    # Restart AW Watchdog
    aw_watchdog_dir = find_aw_watchdog_dir(AW_WATCHDOG_CANDIDATES)

    if not aw_watchdog_dir:
        print("Error: Achievement Watcher Watchdog (nw.exe) was not found in any known location.")
        print("Checked paths:")
        for p in AW_WATCHDOG_CANDIDATES:
            print(f"  - {p}")
        sys.exit(1)

    stop_aw_watchdog()
    time.sleep(2)
    start_aw_watchdog(aw_watchdog_dir)

    print("Achievement Watcher updated successfully!")


if __name__ == "__main__":
    main()
