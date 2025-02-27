# config.py

import os
import requests
from lxml import html

FILE_PATH = "top_owners_ids.txt"

def scrape_top_owner_ids():
    url = "https://steamladder.com/ladder/games/"
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    # Use a relative XPath to target <a> tags in the second table cell
    links = tree.xpath("//table/tbody/tr/td[2]/a/@href")
    user_ids = []
    for link in links:
        parts = [s for s in link.split('/') if s]
        if parts:
            try:
                user_id = int(parts[-1])
                user_ids.append(user_id)
            except ValueError:
                # Skip links where the last part isn't a valid integer
                pass
    # Remove duplicates while preserving order
    return list(dict.fromkeys(user_ids))

# Check if the file exists. If so, load TOP_OWNER_IDS from it.
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as file:
        TOP_OWNER_IDS = [int(line.strip()) for line in file if line.strip()]
else:
    # If the file doesn't exist, scrape and write the IDs to the file.
    TOP_OWNER_IDS = scrape_top_owner_ids()
    with open(FILE_PATH, "w") as file:
        for uid in TOP_OWNER_IDS:
            file.write(f"{uid}\n")

    print("TOP_OWNER_IDS =", TOP_OWNER_IDS)

EXTRA_FEATURES_DISABLE = {
    'configs.main.ini': {
        'main::connectivity': {
            'disable_networking': (1, 'disable all steam networking interface functionality'),
            'disable_source_query': (1, 'do not send server details to the server browser, only works for game servers'),
            'disable_sharing_stats_with_gameserver': (1, 'prevent sharing stats and achievements with any game server, this also disables the interface ISteamGameServerStats'),
        },
    },
}

EXTRA_FEATURES_CONVENIENT = {
    'configs.main.ini': {
        'main::general': {
            'new_app_ticket': (1, 'generate new app auth ticket'),
            'gc_token': (1, 'generate/embed GC token inside new App Ticket'),
            'enable_account_avatar': (1, 'enable avatar functionality'),
        },
        'main::connectivity': {
            'disable_lan_only': (1, 'prevent hooking OS networking APIs and allow any external requests'),
            'share_leaderboards_over_network': (1, 'enable sharing leaderboards scores with people playing the same game on the same network'),
            'download_steamhttp_requests': (1, 'attempt to download external HTTP(S) requests made via Steam_HTTP::SendHTTPRequest()'),
        },
    },
    'configs.overlay.ini': {
        'overlay::general': {
            'enable_experimental_overlay': (1, 'XXX USE AT YOUR OWN RISK XXX, enable the experimental overlay, might cause crashes or other problems'),
            'disable_warning_any': (1, 'disable any warning in the overlay'),
        },
    }
}
