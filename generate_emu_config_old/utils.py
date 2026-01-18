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
