import re
from typing import Dict, Tuple
from utils import create_safe_name


def get_app_name(flag: bool, appid: int, game_info_common: Dict) -> Tuple[str, str]:
    app_name = game_info_common.get("name", "")
    app_name_on_disk = str(appid)

    if app_name:
        print(f"App name on store: '{app_name}'")
        if flag:
            sanitized_name = safe_name.create_safe_name(app_name)
            app_name_on_disk = (
                f"{sanitized_name}-{appid}" if sanitized_name else str(appid)
            )
    else:
        app_name = f"Unknown_Steam_app_{appid}"
        print("[X] Couldn't find app name on store")

    return app_name, app_name_on_disk
