import os
import sys
import json
import shutil
import subprocess
import time

def main():
    # Define the source folder
    src = os.path.join(".", "output")
    if not os.path.exists(src):
        print(r".\output directory doesn't exist. Please run `generate_emu_config.exe` first.")
        sys.exit(1)

    # Define the Achievement Watcher path using the APPDATA environment variable
    aw_path = os.path.join(os.environ.get("APPDATA", ""), "Achievement Watcher")
    if not os.path.exists(aw_path):
        os.makedirs(aw_path, exist_ok=True)

    # Initialize a collection to store the gameIndex data
    game_list = []

    # Process each game's schema folder
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            schema_path = os.path.join(item_path, "Achievement Watcher", "steam_cache", "schema")
            if os.path.exists(schema_path):
                json_path = os.path.join(schema_path, "gameIndex.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            # If the JSON is a list, extend; otherwise, append
                            if isinstance(data, list):
                                game_list.extend(data)
                            else:
                                game_list.append(data)
                    except Exception as e:
                        print(f"Error parsing JSON file {json_path}: {e}")
                        continue

                # Copy everything else from schema_path except the gameIndex.json file
                dest = os.path.join(aw_path, "steam_cache", "schema")
                os.makedirs(dest, exist_ok=True)
                for entry in os.listdir(schema_path):
                    if entry.lower() == "gameindex.json":
                        continue
                    src_item = os.path.join(schema_path, entry)
                    dest_item = os.path.join(dest, entry)
                    if os.path.isdir(src_item):
                        # Merge contents of the source directory into the destination directory
                        os.makedirs(dest_item, exist_ok=True)
                        for file in os.listdir(src_item):
                            src_file = os.path.join(src_item, file)
                            dest_file = os.path.join(dest_item, file)
                            if os.path.isfile(src_file):
                                shutil.copy2(src_file, dest_file)
                    else:
                        shutil.copy2(src_item, dest_item)

    # Sort the game list by appid in descending order
    sorted_list = sorted(game_list, key=lambda x: x.get("appid", 0), reverse=True)
    sorted_json = json.dumps(sorted_list, indent=4)

    # Define paths where gameIndex.json should be saved
    schema_index_path = os.path.join(aw_path, "steam_cache", "schema", "gameIndex.json")
    cfg_index_path = os.path.join(aw_path, "cfg", "gameIndex.json")

    # Ensure destination directories exist
    os.makedirs(os.path.dirname(schema_index_path), exist_ok=True)
    os.makedirs(os.path.dirname(cfg_index_path), exist_ok=True)

    # Export the JSON contents
    with open(schema_index_path, "w", encoding="utf-8") as f:
        f.write(sorted_json)
    with open(cfg_index_path, "w", encoding="utf-8") as f:
        f.write(sorted_json)

    # Restart AW Watchdog
    wd = r"C:\Program Files\Achievement Watcher\nw"
    if not os.path.exists(wd):
        print(f"Error: Achievement Watcher is not installed. Directory '{wd}' does not exist.")
        sys.exit(1)

    print("Stopping AW Watchdog (node.exe)...")
    # Attempt to stop any running node processes
    try:
        import psutil
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
    except ImportError:
        # If psutil is not available, fall back to using taskkill on Windows
        try:
            subprocess.run(["taskkill", "/IM", "node.exe", "/F"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Successfully stopped AW Watchdog.")
        except subprocess.CalledProcessError:
            print("Error: node.exe is not running or could not be stopped.")

    time.sleep(2)

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

    print("Achievement Watcher updated successfully!")

if __name__ == "__main__":
    main()
