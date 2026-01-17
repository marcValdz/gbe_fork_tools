import os
import json
import requests
from typing import Union, List, Dict, Set

def __ClosestDictKey(targetKey: str, srcDict: Union[Dict, Set]) -> Union[str, None]:
    target_lower = targetKey.lower()
    for k in srcDict:
        if k.lower() == target_lower:
            return k
    return None


def __generate_ach_watcher_schema(lang: str, app_id: int, achs: List[Dict]) -> List[Dict]:
    base_icon_url = f'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{app_id}'
    out_achs_list = []

    for ach in achs:
        out_ach = {}

        # Name
        out_ach["name"] = ach.get("name", "")

        # DisplayName
        ach_display = ach.get("displayName")
        if isinstance(ach_display, dict):
            out_ach["displayName"] = ach_display.get(lang) or next(iter(ach_display.values()), "")
        else:
            out_ach["displayName"] = ach_display or ""

        # Description
        ach_desc = ach.get("description")
        if isinstance(ach_desc, dict):
            out_ach["description"] = ach_desc.get(lang) or next(iter(ach_desc.values()), "")
        else:
            out_ach["description"] = ach_desc or ""

        # Hidden flag
        out_ach["hidden"] = int(ach.get("hidden", 0))

        # Icons
        icon_hash = ach.get("icon")
        icongray_hash = ach.get("icongray") or ach.get("icon_gray")
        out_ach["icon"] = f'{base_icon_url}/{icon_hash}' if icon_hash else ""
        out_ach["icongray"] = f'{base_icon_url}/{icongray_hash}' if icongray_hash else ""

        # Copy remaining fields
        for k, v in ach.items():
            if k not in {"name", "displayName", "description", "hidden", "icon", "icongray"}:
                out_ach[k] = v

        out_achs_list.append(out_ach)

    return out_achs_list


def generate_all_ach_watcher_schemas(
    base_out_dir: str,
    appid: int,
    app_name: str,
    app_exe: str,
    achs: List[Dict],
    game_info_common: Dict,
) -> None:
    ach_watcher_out_dir = os.path.join(
        base_out_dir, "Achievement Watcher", "steam_cache", "schema"
    )
    os.makedirs(ach_watcher_out_dir, exist_ok=True)

    print(f"Generating schemas for Achievement Watcher in: {ach_watcher_out_dir}")

    # --------------------------------------------------
    # Store metadata (header + background ONLY)
    # --------------------------------------------------
    try:
        resp = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english",
            timeout=10,
        )
        resp.raise_for_status()
        app_data = resp.json().get(str(appid), {}).get("data", {})
    except Exception as e:
        print(f"[!] Failed to fetch store metadata for {appid}: {e}")
        app_data = {}

    # --------------------------------------------------
    # Icon (community_assets CDN)
    # --------------------------------------------------
    icon_hash = game_info_common.get("icon", "")
    icon_url = (
        f"https://shared.fastly.steamstatic.com/community_assets/images/apps/{appid}/{icon_hash}.jpg"
        if icon_hash
        else ""
    )

    # --------------------------------------------------
    # Base schema
    # --------------------------------------------------
    base_schema = {
        "name": app_name,
        "appid": appid,
        "binary": app_exe,
        "img": {
            "header": app_data.get("header_image", ""),
            "background": app_data.get("background", ""),
            "portrait": "",
            "hero": "",
            "icon": icon_url,
        },
        "achievement": {"total": len(achs)},
    }

    game_index_entry = {
        "appid": appid,
        "name": app_name,
        "binary": app_exe,
        "icon": icon_hash,
    }

    # --------------------------------------------------
    # Detect languages
    # --------------------------------------------------
    langs: Set[str] = set()
    for ach in achs:
        if isinstance(ach.get("displayName"), dict):
            langs.update(ach["displayName"].keys())
        if isinstance(ach.get("description"), dict):
            langs.update(ach["description"].keys())

    langs.discard("token")
    if not langs:
        langs = {"english"}

    # --------------------------------------------------
    # Asset base (store_item_assets CDN)
    # --------------------------------------------------
    asset_base = (
        f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/"
    )

    # --------------------------------------------------
    # Per-language output
    # --------------------------------------------------
    for lang in langs:
        out_dir = os.path.join(ach_watcher_out_dir, lang)
        os.makedirs(out_dir, exist_ok=True)

        schema = base_schema.copy()
        schema["img"] = schema["img"].copy()

        # Portrait
        capsule_img = (
            game_info_common
            .get("library_assets_full", {})
            .get("library_capsule", {})
            .get("image", {})
        )
        capsule_path = capsule_img.get(lang) or capsule_img.get("english")
        if capsule_path:
            schema["img"]["portrait"] = asset_base + capsule_path

        # Hero
        hero_img = (
            game_info_common
            .get("library_assets_full", {})
            .get("library_hero", {})
            .get("image", {})
        )
        hero_path = hero_img.get(lang) or hero_img.get("english")
        if hero_path:
            schema["img"]["hero"] = asset_base + hero_path

        schema["achievement"]["list"] = __generate_ach_watcher_schema(
            lang, appid, achs
        )

        with open(
            os.path.join(out_dir, f"{appid}.db"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

    # --------------------------------------------------
    # gameIndex.json
    # --------------------------------------------------
    with open(
        os.path.join(ach_watcher_out_dir, "gameIndex.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump([game_index_entry], f, ensure_ascii=False, indent=2)
