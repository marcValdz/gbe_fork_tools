# main.py
import os
import sys
import time
import json
import shutil
import difflib
import traceback
import argparse
import textwrap

from steam.client import SteamClient
from steam.webauth import WebAuth
from steam.enums.common import EResult

# Import modules
from utils import get_exe_dir, merge_dict, write_ini_file, create_safe_name
from controller_config_generator import parse_controller_vdf

from external_components.top_owners import TOP_OWNER_IDS
from external_components.app_details import download_app_details
from external_components import app_images, ach_watcher_gen, cdx_gen, cold_client_gen

from args.regen import get_appids_from_output_dir
from args.name import get_app_name, normalize_output_folder
from args.dlc import get_depots_infos
from args.achievements import generate_achievement_stats
from args.inventory import generate_inventory
from args.controller import download_published_file
from args.cloud_dirs import parse_cloud_dirs, get_ufs_dirs
from args.config import EXTRA_FEATURES_DISABLE, EXTRA_FEATURES_CONVENIENT

def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
            This is a command line tool to generate the steam_settings folder for the emu, you need a Steam account to grab most info, but you can use an anonymous account with limited access to Steam data.
        """),
        epilog=textwrap.dedent("""\
            Usage examples:
              %(prog)s 421050 420 480
              %(prog)s -shots -thumbs -vid -imgs -name -cdx -clean -de 421050 480
              %(prog)s -shots -thumbs -vid -imgs -name -cdx -clean -de -cve 421050
              %(prog)s -regen
              
            Automate the login prompt:
              • Create a file called 'my_login.txt' beside the script
                - Line 1: username
                - Line 2: password

              • Or set environment variables (override my_login.txt):
                GSE_CFG_USERNAME
                GSE_CFG_PASSWORD
        """),
    )

    # Positional arguments
    parser.add_argument(
        "appids",
        nargs="*",
        type=int,
        help="One or more Steam App IDs"
    )

    # Login / auth
    parser.add_argument("-anon", action="store_true", help="Login as anonymous account (limited access)")
    parser.add_argument("-token", action="store_true", help="Save refresh token to disk after login")

    # Steam Store API
    parser.add_argument("-shots", action="store_true", help="Download screenshots for each app if available")
    parser.add_argument("-thumbs", action="store_true", help="Download screenshot thumbnails if available")
    parser.add_argument("-vid", action="store_true", help="Download the first available video")
    parser.add_argument("-imgs", action="store_true", help="Download common images (background, icon, logo, etc.)")

    # Skip flags
    parser.add_argument("-skip_dlc", action="store_true", help="Skip downloadable content info generation")
    parser.add_argument("-skip_ach", action="store_true", help="Skip achievements and Achievement Watcher schema generation")
    parser.add_argument("-skip_con", action="store_true", help="Skip controller configuration generation")
    parser.add_argument("-skip_inv", action="store_true", help="Skip inventory data generation")
    parser.add_argument("-skip_cld", action="store_true", help="Skip parsing directories for cloud saves")

    # Output / generation
    parser.add_argument("-name", action="store_true", help="Save output in a folder named after the app")
    parser.add_argument("-reldir", action="store_true", help="Use relative directories for temp/input files")
    parser.add_argument("-clean", action="store_true", help="Clean output folder before generating data")
    parser.add_argument("-regen", action="store_true", help="Regenerate configs for all tracked app IDs")

    # Extras
    parser.add_argument("-de", action="store_true", help="Disable extra features")
    parser.add_argument("-cve", action="store_true", help="Enable convenient extra features")
    parser.add_argument("-cdx", action="store_true", help="Generate CODEX and ColdClient Steam emu .ini files")

    args = parser.parse_args()

    # Start with explicitly provided appids
    appids = set(args.appids)

    # If regenerating, augment with tracked appids
    if args.regen:
        appids.update(get_appids_from_output_dir())

    # If nothing to do, decide why and exit once
    if not appids:
        if args.regen:
            print("[X] No appid folders found in output/.")
        else:
            parser.print_help()
        sys.exit(1)

    USERNAME = ""
    PASSWORD = ""
    
    # Currently, it's not possible to generate achievement/stat information (schema and .json) with an anonymous login.
    # It's theoretically possible to fetch this information with an API key using the steam web API pathway instead.
    if (args.anon): args.skip_ach = True

    client = SteamClient()
    if args.anon:
        result = client.anonymous_login()
        trials = 5
        while result != EResult.OK and trials > 0:
            time.sleep(1)
            result = client.anonymous_login()
            trials -= 1
    else:
        my_login_file = os.path.join(get_exe_dir(args.reldir), "my_login.txt")
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

        REFRESH_TOKENS = os.path.join(get_exe_dir(args.reldir), "refresh_tokens.json")
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
                if PROMPT_FOR_UNAVAILABLE and result == EResult.ServiceUnavailable:
                    answer = input("Steam is down. Keep retrying? [y/n]: ").lower()
                    PROMPT_FOR_UNAVAILABLE = False
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
            print(f"Login result: {result}")
            print(f"Client connected after login: {client.connected}")

        if result != EResult.OK:
            if REFRESH_TOKEN:
                print("Login failed, refresh token may be stale. Removing it. Please run the script again to re-authenticate.")
                if USERNAME in refresh_tokens:
                    del refresh_tokens[USERNAME]
                    with open(REFRESH_TOKENS, 'w') as f:
                        json.dump(refresh_tokens, f, indent=4)
                sys.exit(1)
            else:
                print(f"Login failed with result: {result}")
                sys.exit(1)

        if args.token:
            with open(REFRESH_TOKENS, 'w') as f:
                refresh_tokens.update({USERNAME: REFRESH_TOKEN})
                json.dump(refresh_tokens, f, indent=4)

    # Prepend additional owner IDs from file if available
    top_owners_file = os.path.join(get_exe_dir(args.reldir), "top_owners_ids.txt")
    if os.path.isfile(top_owners_file):
        with open(top_owners_file, "r", encoding="utf-8") as f:
            filedata = [line.strip() for line in f if line.strip().isdigit()]
        all_ids = list(map(int, filedata))
        TOP_OWNER_IDS[:0] = all_ids

    if not args.anon:
        TOP_OWNER_IDS.insert(0, client.steam_id.as_64)

    for appid in appids:
        out_config_app_ini = {}
        print(f"********* Generating info for app id {appid} *********")
        raw = client.get_product_info(apps=[appid])
        game_info = raw["apps"][appid]
        game_info_common = game_info.get("common", {})
        
        app_name, app_name_on_disk = get_app_name(args.name, appid, game_info_common)
        root_out_dir = "output"
        normalize_output_folder(root_out_dir, appid, app_name_on_disk)
        
        base_out_dir = os.path.join(root_out_dir, app_name_on_disk)
        emu_settings_dir = os.path.join(base_out_dir, "steam_settings")
        info_out_dir = os.path.join(base_out_dir, "info")
        
        root_backup_dir = os.path.join(get_exe_dir(args.reldir), "backup")
        backup_dir = os.path.join(root_backup_dir, f"{appid}")
        os.makedirs(backup_dir, exist_ok=True)

        if args.clean:
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
        
        app_details = download_app_details(
            base_out_dir, info_out_dir,
            appid,
            args.shots,
            args.thumbs,
            args.vid)

        achievements = []
        stats = []
        languages = []
        app_exe = ''

        if game_info_common:
            if not args.skip_ach:
                # The stats information can be returned from this function, but we can't really use it anywhere else at the moment.
                # Unlike achievements which is later passed into the achievement watcher schema generation function.
                achievements, stats = generate_achievement_stats(client, appid, emu_settings_dir, backup_dir, TOP_OWNER_IDS)
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
        dlc_list, depot_app_list, all_depots, all_branches = get_depots_infos(args.skip_dlc, game_info)
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
            if not args.skip_con and "steamcontrollerconfigdetails" in game_info["config"]:
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
            if not args.skip_con and "steamcontrollertouchconfigdetails" in game_info["config"]:
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
        
        if not args.skip_ach:
            ach_watcher_gen.generate_all_ach_watcher_schemas(
                base_out_dir,
                appid,
                app_name,
                app_exe,
                achievements,
                app_details,
                game_info_common)
        
        if args.cdx:
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
        
        if args.imgs:
            app_images.download_app_images(
                base_out_dir,
                appid,
                game_info_common)

        if not args.skip_cld:
            (save_files, save_file_overrides) = parse_cloud_dirs(game_info)

            win_cloud_dirs = get_ufs_dirs("Windows", save_files, save_file_overrides)
            for idx in range(len(win_cloud_dirs)):
                merge_dict(out_config_app_ini, {
                    'configs.app.ini': {
                        'app::cloud_save::win': {
                            f"dir{idx + 1}": (win_cloud_dirs[idx], ''),
                        }
                    }
                })

            linux_cloud_dirs = get_ufs_dirs("Linux", save_files, save_file_overrides)
            for idx in range(len(linux_cloud_dirs)):
                merge_dict(out_config_app_ini, {
                    'configs.app.ini': {
                        'app::cloud_save::linux': {
                            f"dir{idx + 1}": (linux_cloud_dirs[idx], ''),
                        }
                    }
                })

        if args.de:
            merge_dict(out_config_app_ini, EXTRA_FEATURES_DISABLE)
        if args.cve:
            merge_dict(out_config_app_ini, EXTRA_FEATURES_CONVENIENT)
        if out_config_app_ini:
            write_ini_file(emu_settings_dir, out_config_app_ini)

        inventory_data = None
        if not args.skip_inv:
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
