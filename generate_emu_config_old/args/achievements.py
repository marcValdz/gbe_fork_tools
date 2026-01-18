# achievements.py
import os
import time
import threading
import queue
import requests
import sys
import traceback
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from stats_schema_achievement_gen import achievements_gen


def get_stats_schema(client, game_id, owner_id):
    message = MsgProto(EMsg.ClientGetUserStats)
    message.body.game_id = game_id
    message.body.schema_local_version = -1
    message.body.crc_stats = 0
    message.body.steam_id_for_user = owner_id

    client.send(message)
    return client.wait_msg(EMsg.ClientGetUserStatsResponse, timeout=5)


def download_achievement_images(game_id: int, image_names: set, output_folder: str):
    print(f"Downloading achievement images in '{output_folder}', count = {len(image_names)}")
    q = queue.Queue()

    def downloader_thread():
        while True:
            name = q.get()
            if name is None:
                q.task_done()
                return
            succeeded = False
            # Updated CDN endpoints
            for base_url in [
                "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/",
                "https://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/"
            ]:
                # If the image name is already a full URL, just use it directly
                url = name if name.startswith("http") else f"{base_url}{game_id}/{name}"
                try:
                    response = requests.get(url, allow_redirects=True, timeout=10)
                    response.raise_for_status()
                    with open(os.path.join(output_folder, os.path.basename(name)), "wb") as f:
                        f.write(response.content)
                    succeeded = True
                    break
                except Exception as e:
                    print(f"HTTPError downloading {url}", file=sys.stderr)
                    traceback.print_exception(e, file=sys.stderr)
            if not succeeded:
                print("Error: could not download", name)
            q.task_done()

    num_threads = 50
    for _ in range(num_threads):
        threading.Thread(target=downloader_thread, daemon=True).start()

    for name in image_names:
        q.put(name)
    q.join()

    # Signal threads to exit
    for _ in range(num_threads):
        q.put(None)
    q.join()
    print("Finished downloading achievement images")


def generate_achievement_stats(client, game_id: int, output_directory, backup_directory, top_owner_ids) -> list:
    stats_schema_found = None
    print("Finding achievement stats...")
    for owner_id in top_owner_ids:
        print(f"Trying account ID {owner_id} for achievement stats...")
        out = get_stats_schema(client, game_id, owner_id)
        if out is not None and len(out.body.schema) > 0:
            stats_schema_found = out
            print(f"Found achievement stats using account ID {owner_id}!")
            break

    if stats_schema_found is None:
        print(f"[X] App id {game_id} has no achievements")
        return []

    achievement_images_dir = os.path.join(output_directory, "img")
    images_to_download = set()

    # Backup schema
    with open(os.path.join(backup_directory, f'UserGameStatsSchema_{game_id}.bin'), 'wb') as f:
        f.write(stats_schema_found.body.schema)

    achievements, stats, copy_default_unlocked_img, copy_default_locked_img = \
        achievements_gen.generate_stats_achievements(stats_schema_found.body.schema, output_directory)
    
    for ach in achievements:
        icon = str(ach.get('icon', '')).strip()
        if icon:
            images_to_download.add(icon)
        icon_gray = str(ach.get('icon_gray', '')).strip()
        if icon_gray:
            images_to_download.add(icon_gray)

    if images_to_download:
        if not os.path.exists(achievement_images_dir):
            os.makedirs(achievement_images_dir)
        if copy_default_unlocked_img:
            import shutil
            from utils import get_exe_dir
            shutil.copy(os.path.join(get_exe_dir(), "steam_default_icon_unlocked.jpg"), achievement_images_dir)
        if copy_default_locked_img:
            import shutil
            from utils import get_exe_dir
            shutil.copy(os.path.join(get_exe_dir(), "steam_default_icon_locked.jpg"), achievement_images_dir)
        download_achievement_images(game_id, images_to_download, achievement_images_dir)

    return achievements
