import re
import os
from typing import Dict, Tuple
from utils import create_safe_name


def normalize_output_folder(output_root, appid, desired_name):
    """
    Ensure exactly one folder exists for this appid, named `desired_name`.
    Any other folders resolving to this appid are removed or migrated.
    """
    existing = []

    if not os.path.isdir(output_root):
        return

    for name in os.listdir(output_root):
        path = os.path.join(output_root, name)
        if not os.path.isdir(path):
            continue

        resolved = None
        if name.isdigit():
            resolved = int(name)
        elif '-' in name:
            tail = name.rsplit('-', 1)[-1]
            if tail.isdigit():
                resolved = int(tail)

        if resolved == appid:
            existing.append(name)

    if not existing:
        return

    desired_path = os.path.join(output_root, desired_name)

    # If desired folder already exists, delete all others
    if desired_name in existing:
        for name in existing:
            if name != desired_name:
                shutil.rmtree(os.path.join(output_root, name))
        return

    # Otherwise, migrate the first existing folder
    src = os.path.join(output_root, existing[0])
    os.rename(src, desired_path)

    for name in existing[1:]:
        shutil.rmtree(os.path.join(output_root, name))


def get_app_name(flag: bool, appid: int, game_info_common: Dict) -> Tuple[str, str]:
    app_name = game_info_common.get("name", "")
    app_name_on_disk = str(appid)

    if app_name:
        print(f"App name on store: '{app_name}'")
        if flag:
            sanitized_name = create_safe_name(app_name)
            app_name_on_disk = (
                f"{sanitized_name}-{appid}" if sanitized_name else str(appid)
            )
    else:
        app_name = f"Unknown_Steam_app_{appid}"
        print("[X] Couldn't find app name on store")

    return app_name, app_name_on_disk
