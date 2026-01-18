# config.py
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
