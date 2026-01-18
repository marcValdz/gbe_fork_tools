import os

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
