# utils.py
import os
import sys
import pathlib

def get_exe_dir(relative=False):
    if relative:
        return os.path.curdir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def merge_dict(dest: dict, src: dict):
    for key, value in src.items():
        if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
            merge_dict(dest[key], value)
        else:
            dest[key] = value

def write_ini_file(base_path: str, out_ini: dict):
    for filename, sections in out_ini.items():
        file_path = os.path.join(base_path, filename)
        with open(file_path, 'wt', encoding='utf-8') as f:
            for section, items in sections.items():
                f.write(f'[{section}]\n')
                for key, (val, comment) in items.items():
                    if comment:
                        f.write(f'# {comment}\n')
                    f.write(f'{key}={val}\n')
                f.write('\n')

def print_help():
    exe_name = os.path.basename(sys.argv[0])
    help_text = f"""
Usage: {exe_name} [Switches] appid appid appid ...
 Example: {exe_name} 421050 420 480
 Example: {exe_name} -shots -thumbs -vid -imgs -name -cdx -aw -clean -de 421050 480
 Example: {exe_name} -shots -thumbs -vid -imgs -name -cdx -aw -clean -de -cve 421050

Switches:
 -shots:    download screenshots for each app if available
 -thumbs:   download screenshot thumbnails if available
 -vid:      download the first available video (trailer, gameplay, etc.)
 -imgs:     download common images (background, icon, logo, etc.)
 -name:     save output in a folder named after the app (unsafe characters are removed)
 -cdx:      generate .ini file for CODEX Steam emu for each app
 -clean:    clean output folder before generating data
 -anon:     login as an anonymous account (limited access)
 -token:    save refresh_token to disk after login
 -de:       disable some extra features (by generating corresponding config files)
 -cve:      enable convenient extra features (by generating corresponding config files)
 -reldir:   use relative directories for temp/input files
 -skip_ach: skip achievements processing and Achievement Watcher schema generation
 -skip_con: skip controller configuration generation
 -skip_inv: skip inventory data generation
"""
    print(help_text)
