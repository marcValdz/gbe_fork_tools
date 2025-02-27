# inventory.py
import os
import json
import requests
import sys
import traceback
from steam.enums.common import EResult

def get_inventory_info(client, game_id):
    return client.send_um_and_wait('Inventory.GetItemDefMeta#1', {
        'appid': game_id
    })

def generate_inventory(client, game_id):
    inventory = get_inventory_info(client, game_id)
    if inventory.header.eresult != EResult.OK:
        return None

    url = f"https://api.steampowered.com/IGameInventory/GetItemDefArchive/v0001?appid={game_id}&digest={inventory.body.digest}"
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading from '{url}'", file=sys.stderr)
        traceback.print_exception(e, file=sys.stderr)
    return None
