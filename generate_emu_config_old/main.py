# main.py
import os
import sys
import time
import json
import shutil
import difflib
import traceback

from steam.client import SteamClient
from steam.webauth import WebAuth
from steam.enums.common import EResult

# Import modules
from config import TOP_OWNER_IDS, EXTRA_FEATURES_DISABLE, EXTRA_FEATURES_CONVENIENT
from utils import get_exe_dir, merge_dict, write_ini_file, print_help
from achievements import generate_achievement_stats
from published_files import download_published_file
from inventory import generate_inventory
from depots import get_depots_infos
from external_components import app_details, app_images, safe_name
from controller_config_generator import parse_controller_vdf
from external_components import ach_watcher_gen, cdx_gen, cold_client_gen

def get_appids_from_output_dir():
    """Scan the output directory for subfolders and extract appids from their names."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        return set()
    appids = set()
    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)
        if not os.path.isdir(path):
            continue
        # Try to extract appid from folder name
        if '-' in name:
            possible_appid = name.rsplit('-', 1)[-1]
            if possible_appid.isdigit():
                appids.add(int(possible_appid))
                continue
        if name.isdigit():
            appids.add(int(name))
    return appids

def main():
    # Initialize flags and login variables
    USERNAME = ""
    PASSWORD = ""
    
    DISABLE_EXTRA = False
    CONVENIENT_EXTRA = False
    DOWNLOAD_SCREESHOTS = False
    DOWNLOAD_THUMBNAILS = False
    DOWNLOAD_VIDEOS = False
    DOWNLOAD_COMMON_IMAGES = False
    SAVE_APP_NAME = False
    GENERATE_CODEX_INI = False
    CLEANUP_BEFORE_GENERATING = False
    ANON_LOGIN = False
    SAVE_REFRESH_TOKEN = False
    RELATIVE_DIR = False
    SKIP_ACHIEVEMENTS = False
    SKIP_CONTROLLER = False
    SKIP_INVENTORY = False
    REGENERATE = False
    
    prompt_for_unavailable = True

    appids = set()
    for arg in sys.argv[1:]:
        lower_arg = arg.lower()
        if arg.isnumeric():
            appids.add(int(arg))
        elif lower_arg == '-shots':
            DOWNLOAD_SCREESHOTS = True
        elif lower_arg == '-thumbs':
            DOWNLOAD_THUMBNAILS = True
        elif lower_arg == '-vid':
            DOWNLOAD_VIDEOS = True
        elif lower_arg == '-imgs':
            DOWNLOAD_COMMON_IMAGES = True
        elif lower_arg == '-name':
            SAVE_APP_NAME = True
        elif lower_arg == '-cdx':
            GENERATE_CODEX_INI = True
        elif lower_arg == '-clean':
            CLEANUP_BEFORE_GENERATING = True
        elif lower_arg == '-anon':
            ANON_LOGIN = True
        elif lower_arg == '-token':
            SAVE_REFRESH_TOKEN = True
        elif lower_arg == '-de':
            DISABLE_EXTRA = True
        elif lower_arg == '-cve':
            CONVENIENT_EXTRA = True
        elif lower_arg == '-reldir':
            RELATIVE_DIR = True
        elif lower_arg == '-skip_ach':
            SKIP_ACHIEVEMENTS = True
        elif lower_arg == '-skip_con':
            SKIP_CONTROLLER = True
        elif lower_arg == '-skip_inv':
            SKIP_INVENTORY = True
        elif lower_arg == '-regen':
            REGENERATE = True
        else:
            print(f'[X] Invalid switch: {arg}')
            print_help()
            sys.exit(1)
    
    # If -regen is specified, get all appids from output folder names
    if REGENERATE:
        appids.update(get_appids_from_output_dir())
    
    if not appids:
        if not REGENERATE:
            print('[X] No app id was provided')
            print_help()
            sys.exit(1)
        else:
            print('[X] No appid folders found in output/.')
            sys.exit(1)

    client = SteamClient()
    if ANON_LOGIN:
        result = client.anonymous_login()
        trials = 5
        while result != EResult.OK and trials > 0:
            time.sleep(1)
            result = client.anonymous_login()
            trials -= 1
    else:
        my_login_file = os.path.join(get_exe_dir(RELATIVE_DIR), "my_login.txt")
        if os.path.isfile(my_login_file):
            with open(my_login_file, "r", encoding="utf-8") as f:
                filedata = [line.strip() for line in f if line.strip()]
            if len(filedata) == 1:
                USERNAME = filedata[0]
            elif len(filedata) == 2:
                USERNAME, PASSWORD = filedata[0], filedata[1]
        
        env_username = os.environ.get('GSE_CFG_USERNAME')
        env_password = os.environ.get('GSE_CFG_PASSWORD')
        if env_username:
            USERNAME = env_username
        if env_password:
            PASSWORD = env_password

        REFRESH_TOKENS = os.path.join(get_exe_dir(RELATIVE_DIR), "refresh_tokens.json")
        refresh_tokens = {}
        if os.path.isfile(REFRESH_TOKENS):
            with open(REFRESH_TOKENS) as f:
                try:
                    data = json.load(f)
                    refresh_tokens = data if isinstance(data, dict) else {}
                except:
                    pass

        if not USERNAME:
            users = {i: user for i, user in enumerate(refresh_tokens, 1)}
            if users:
                for i, user in users.items():
                    print(f"{i}: {user}")
                while True:
                    try:
                        num = int(input("Choose an account to login (0 for add account): "))
                    except ValueError:
                        print('Please type a number')
                        continue
                    break
                USERNAME = users.get(num, "")
        if not USERNAME:
            USERNAME = input("Steam user: ")

        REFRESH_TOKEN = refresh_tokens.get(USERNAME)
        webauth = WebAuth()
        result = None
        while result in (EResult.TryAnotherCM, EResult.ServiceUnavailable, EResult.InvalidPassword, None):
            if result in (EResult.TryAnotherCM, EResult.ServiceUnavailable):
                if prompt_for_unavailable and result == EResult.ServiceUnavailable:
                    answer = input("Steam is down. Keep retrying? [y/n]: ").lower()
                    prompt_for_unavailable = False
                    if answer.startswith('n'):
                        break
                client.reconnect(maxdelay=15)
            elif result == EResult.InvalidPassword:
                print("Invalid password or refresh_token. Correct the details or delete the refresh token file and try again.")
                sys.exit(1)

            if not REFRESH_TOKEN:
                try:
                    webauth.cli_login(USERNAME, PASSWORD)
                except Exception as e:
                    print(f'Error during login: {e}')
                    sys.exit(1)
                USERNAME, PASSWORD = webauth.username, webauth.password
                REFRESH_TOKEN = webauth.refresh_token

            result = client.login(USERNAME, PASSWORD, REFRESH_TOKEN)

        if SAVE_REFRESH_TOKEN:
            with open(REFRESH_TOKENS, 'w') as f:
                refresh_tokens.update({USERNAME: REFRESH_TOKEN})
                json.dump(refresh_tokens, f, indent=4)

    # Prepend additional owner IDs from file if available
    top_owners_file = os.path.join(get_exe_dir(RELATIVE_DIR), "top_owners_ids.txt")
    if os.path.isfile(top_owners_file):
        with open(top_owners_file, "r", encoding="utf-8") as f:
            filedata = [line.strip() for line in f if line.strip().isdigit()]
        all_ids = list(map(int, filedata))
        TOP_OWNER_IDS[:0] = all_ids

    if not ANON_LOGIN:
        TOP_OWNER_IDS.insert(0, client.steam_id.as_64)

    for appid in appids:
        out_config_app_ini = {}
        print(f"********* Generating info for app id {appid} *********")
        raw = client.get_product_info(apps=[appid])
        game_info = raw["apps"][appid]
        game_info_common = game_info.get("common", {})
        app_name = game_info_common.get("name", "")
        app_name_on_disk = f"{appid}"
        if app_name:
            print(f"App name on store: '{app_name}'")
            if SAVE_APP_NAME:
                sanitized_name = safe_name.create_safe_name(app_name)
                if sanitized_name:
                    app_name_on_disk = f'{sanitized_name}-{appid}'
        else:
            app_name = f"Unknown_Steam_app_{appid}" # we need this for later use in the Achievement Watcher
            print("[X] Couldn't find app name on store")

        root_backup_dir = os.path.join(get_exe_dir(RELATIVE_DIR), "backup")
        backup_dir = os.path.join(root_backup_dir, f"{appid}")
        os.makedirs(backup_dir, exist_ok=True)

        root_out_dir = "output"
        base_out_dir = os.path.join(root_out_dir, app_name_on_disk)
        emu_settings_dir = os.path.join(base_out_dir, "steam_settings")
        info_out_dir = os.path.join(base_out_dir, "info")

        if CLEANUP_BEFORE_GENERATING:
            print("Cleaning output folder before generating data")
            if os.path.exists(base_out_dir):
                shutil.rmtree(base_out_dir)
                while os.path.exists(base_out_dir):
                    time.sleep(0.05)

        os.makedirs(emu_settings_dir, exist_ok=True)
        os.makedirs(info_out_dir, exist_ok=True)

        print(f"Output dir: '{base_out_dir}'")
        with open(os.path.join(info_out_dir, "product_info.json"), "w", encoding='utf-8') as f:
            json.dump(game_info, f, ensure_ascii=False, indent=2)
        
        app_details.download_app_details(
            base_out_dir, info_out_dir,
            appid,
            DOWNLOAD_SCREESHOTS,
            DOWNLOAD_THUMBNAILS,
            DOWNLOAD_VIDEOS)

        clienticon = game_info_common.get("clienticon")
        icon = game_info_common.get("icon")
        logo = game_info_common.get("logo")
        logo_small = game_info_common.get("logo_small")
        achievements = []
        languages = []
        app_exe = ''

        if game_info_common:
            if not SKIP_ACHIEVEMENTS:
                achievements = generate_achievement_stats(client, appid, emu_settings_dir, backup_dir, TOP_OWNER_IDS)
            if "supported_languages" in game_info_common:
                langs = game_info_common["supported_languages"]
                for lang in langs:
                    if str(langs[lang].get("supported", "")).lower() in ["true", "1"]:
                        languages.append(lang.lower())
        if languages:
            with open(os.path.join(emu_settings_dir, "supported_languages.txt"), 'w', encoding='utf-8') as f:
                for lang in languages:
                    f.write(f'{lang}\n')
        
        with open(os.path.join(emu_settings_dir, "steam_appid.txt"), 'w') as f:
            f.write(str(appid))

        dlc_config_list = []
        dlc_list, depot_app_list, all_depots, all_branches = get_depots_infos(game_info)
        dlc_raw = {}
        if dlc_list:
            dlc_raw = client.get_product_info(apps=dlc_list)["apps"]
            for dlc in dlc_raw:
                try:
                    dlc_name = dlc_raw[dlc]["common"].get("name", "")
                except Exception:
                    dlc_name = ""
                if not dlc_name:
                    dlc_name = f"Unknown Steam app {dlc}"
                dlc_config_list.append((dlc, dlc_name))

        # we set unlock_all=0 nonetheless, to make the emu lock DLCs, otherwise everything is allowed
        # some games use that as a detection mechanism
        merge_dict(out_config_app_ini, {
            'configs.app.ini': {
                'app::dlcs': {
                    'unlock_all': (0, 'should the emu report all DLCs as unlocked, default=1'),
                }
            }
        })
        for x in dlc_config_list:
            merge_dict(out_config_app_ini, {
                'configs.app.ini': {
                    'app::dlcs': {
                        x[0]: (x[1], ''),
                    }
                }
            })
        # write the data as soon as possible in case a later step caused an exception
        write_ini_file(emu_settings_dir, out_config_app_ini)

        if all_depots:
            with open(os.path.join(emu_settings_dir, "depots.txt"), 'w', encoding="utf-8") as f:
                for depot in all_depots:
                    f.write(f"{depot}\n")
        
        if all_branches:
            with open(os.path.join(emu_settings_dir, "branches.json"), "w", encoding='utf-8') as f:
                json.dump(all_branches, f, ensure_ascii=False, indent=2)

        config_generated = False
        if "config" in game_info:
            if not SKIP_CONTROLLER and "steamcontrollerconfigdetails" in game_info["config"]:
                controller_details = game_info["config"]["steamcontrollerconfigdetails"]
                print('Downloading controller vdf files')
                for id in controller_details:
                    details = controller_details[id]
                    controller_type = details.get("controller_type", "")
                    enabled_branches = details.get("enabled_branches", "")
                    print(f'Downloading controller data, file id = {id}, controller type = {controller_type}')
                    out_vdf = download_published_file(client, int(id), os.path.join(backup_dir, f'{controller_type}-{id}'))
                    if out_vdf is not None and not config_generated:
                        if (controller_type in ["controller_xbox360", "controller_xboxone", "controller_steamcontroller_gordon"] and
                            (("default" in enabled_branches) or ("public" in enabled_branches))):
                            print('Controller type supported')
                            parse_controller_vdf.generate_controller_config(out_vdf.decode('utf-8'), os.path.join(emu_settings_dir, "controller"))
                            config_generated = True
            if not SKIP_CONTROLLER and "steamcontrollertouchconfigdetails" in game_info["config"]:
                controller_details = game_info["config"]["steamcontrollertouchconfigdetails"]
                for id in controller_details:
                    details = controller_details[id]
                    controller_type = details.get("controller_type", "")
                    print(id, controller_type)
                    download_published_file(client, int(id), os.path.join(backup_dir, controller_type + str(id)))
            if "launch" in game_info["config"]:
                launch_configs = game_info["config"]["launch"]
                possible_executables = []
                for cfg_id, cfg in launch_configs.items():
                    app_exe = cfg.get("executable", "")
                    if app_exe.lower().endswith(".exe"):
                        exe_name = app_exe.replace("\\", "/").split('/')[-1]
                        config = cfg.get("config", {})
                        possible_executables.append((exe_name, config.get("osarch") == "64", "betakey" in config))
                with open(os.path.join(info_out_dir, "launch_config.json"), "w", encoding='utf-8') as f:
                    json.dump(launch_configs, f, ensure_ascii=False, indent=2)
                if len(possible_executables) == 1:
                    app_exe = possible_executables[0][0]
                    print(f"Chose the only executable: {app_exe}")
                elif possible_executables:
                    preferred_exes = [exe for exe in possible_executables if not exe[2] and exe[1]]
                    if preferred_exes:
                        app_exe = preferred_exes[0][0]
                    else:
                        game_name = game_info["common"]["name"].lower().replace(" ", "")
                        def similarity_score(exe):
                            return difflib.SequenceMatcher(None, exe[0].lower().replace(" ", ""), game_name).ratio()
                        app_exe = max(possible_executables, key=similarity_score)[0]
                else:
                    app_exe = ""
        
        if not SKIP_ACHIEVEMENTS:
            ach_watcher_gen.generate_all_ach_watcher_schemas(
                base_out_dir,
                appid,
                app_name,
                app_exe,
                achievements,
                icon)
        
        if GENERATE_CODEX_INI:
            user_id3 = client.steam_id.as_steam3.split(":")[2][:-1]
            username = client.user.name or "Player"
            cdx_gen.generate_cdx_ini(
                base_out_dir,
                appid,
                user_id3,
                username,
                dlc_config_list,
                achievements)
            cold_client_gen.generate_cold_client_ini(
                base_out_dir,
                appid,
                app_exe)
        
        if DOWNLOAD_COMMON_IMAGES:
            app_images.download_app_images(
                base_out_dir,
                appid,
                clienticon,
                icon,
                logo,
                logo_small)
        
        if DISABLE_EXTRA:
            merge_dict(out_config_app_ini, EXTRA_FEATURES_DISABLE)
        if CONVENIENT_EXTRA:
            merge_dict(out_config_app_ini, EXTRA_FEATURES_CONVENIENT)
        if out_config_app_ini:
            write_ini_file(emu_settings_dir, out_config_app_ini)

        inventory_data = None
        if not SKIP_INVENTORY:
            inventory_data = generate_inventory(client, appid)
        if inventory_data is not None:
            out_inventory = {}
            default_items = {}
            inventory = json.loads(inventory_data.rstrip(b"\x00"))
            with open(os.path.join(backup_dir, "inventory.json"), "w") as f:
                f.write(json.dumps(inventory, indent=4))
            for i in inventory:
                index = str(i["itemdefid"])
                x = {}
                for key, value in i.items():
                    if value is True:
                        x[key] = "true"
                    elif value is False:
                        x[key] = "false"
                    else:
                        x[key] = str(value)
                out_inventory[index] = x
                default_items[index] = {"quantity": 1}
            with open(os.path.join(emu_settings_dir, "items.json"), "w", encoding='utf-8') as f:
                json.dump(out_inventory, f, ensure_ascii=False, indent=2)
            with open(os.path.join(emu_settings_dir, "default_items.json"), "w", encoding='utf-8') as f:
                json.dump(default_items, f, ensure_ascii=False, indent=2)

        with open(os.path.join(backup_dir, "product_info.json"), "w", encoding='utf-8') as f:
            json.dump(game_info, f, ensure_ascii=False, indent=2)
        with open(os.path.join(backup_dir, "dlc_product_info.json"), "w", encoding='utf-8') as f:
            json.dump(dlc_raw, f, ensure_ascii=False, indent=2)
        
        print(f"######### Done for app id {appid} #########\n\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Unexpected error:")
        print(e)
        print("-----------------------")
        traceback.print_exception(e)
        print("-----------------------")
        sys.exit(1)
