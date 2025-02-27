# published_files.py
import os
import requests
import sys
import traceback
from steam.enums.common import EResult

def get_ugc_info(client, published_file_id):
    return client.send_um_and_wait('PublishedFile.GetDetails#1', {
        'publishedfileids': [published_file_id],
        'includetags': False,
        'includeadditionalpreviews': False,
        'includechildren': False,
        'includekvtags': False,
        'includevotes': False,
        'short_description': True,
        'includeforsaledata': False,
        'includemetadata': False,
        'language': 0
    })

def download_published_file(client, published_file_id, backup_directory):
    ugc_info = get_ugc_info(client, published_file_id)
    if ugc_info is None:
        print("Failed getting published file", published_file_id)
        return None

    file_details = ugc_info.body.publishedfiledetails[0]
    if file_details.result != EResult.OK:
        print("Failed getting published file", published_file_id, file_details.result)
        return None

    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    with open(os.path.join(backup_directory, "info.txt"), "w") as f:
        f.write(str(ugc_info.body))

    if file_details.file_url:
        try:
            response = requests.get(file_details.file_url, allow_redirects=True)
            response.raise_for_status()
            data = response.content
            safe_filename = file_details.filename.replace("/", "_").replace("\\", "_")
            with open(os.path.join(backup_directory, safe_filename), "wb") as f:
                f.write(data)
            return data
        except Exception as e:
            print(f"Error downloading from '{file_details.file_url}'", file=sys.stderr)
            traceback.print_exception(e, file=sys.stderr)
            return None
    else:
        print("Could not download file", published_file_id, "- no URL provided")
        return None
