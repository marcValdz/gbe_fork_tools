# config.py

'''
import requests
from lxml import html

url = "https://steamladder.com/ladder/games/"
response = requests.get(url)
response.raise_for_status()

# Parse the HTML content
tree = html.fromstring(response.content)

# Use a relative XPath to find all href attributes for the <a> tags in the second table cell
links = tree.xpath("//table/tbody/tr/td[2]/a/@href")

user_ids = []
for link in links:
    parts = [s for s in link.split('/') if s]
    if parts:
        try:
            user_id = int(parts[-1])
            user_ids.append(user_id)
        except ValueError:
            # Skip if conversion to int fails
            pass

# Remove duplicates while preserving order
TOP_OWNER_IDS = list(dict.fromkeys(user_ids))
print("TOP_OWNER_IDS =", TOP_OWNER_IDS)

# Export all the Steam IDs to a text file, one per line
with open("top_owners_ids.txt", "w") as file:
    for id in TOP_OWNER_IDS:
        file.write(f"{id},\n")
'''

TOP_OWNER_IDS = list(dict.fromkeys([
    76561198028121353,
    76561198017975643,
    76561197979911851,
    76561198355953202,
    76561197993544755,
    76561198355625888,
    76561198001237877,
    76561198152618007,
    76561198237402290,
    76561198213148949,
    # 76561198217186687,
    # 76561197969050296,
    # 76561198001678750,
    # 76561198037867621,
    # 76561198094227663,
    # 76561198019712127,
    # 76561197973009892,
    # 76561197963550511,
    # 76561198134044398,
    # 76561197976597747,
    # 76561198044596404,
    # 76561197969810632,
    # 76561197962473290,
    # 76561197995070100,
    # 76561198085065107,
    # 76561198095049646,
    # 76561198313790296,
    # 76561198033715344,
    # 76561197996432822,
    # 76561198388522904,
    # 76561198063574735,
    # 76561198119667710,
    # 76561198027214426,
    # 76561198281128349,
    # 76561198035900006,
    # 76561198154462478,
    # 76561197970825215,
    # 76561197976968076,
    # 76561198235911884,
    # 76561198842864763,
    # 76561198027233260,
    # 76561198256917957,
    # 76561198122859224,
    # 76561198104323854,
    # 76561198010615256,
    # 76561198062901118,
    # 76561198001221571,
    # 76561198008181611,
    # 76561197974742349,
    # 76561197968410781,
    # 76561198077213101,
    # 76561199492215670,
    # 76561198082995144,
    # 76561197979667190,
    # 76561198407953371,
    # 76561197990233857,
    # 76561199130977924,
    # 76561198158932704,
    # 76561198063728345,
    # 76561198121398682,
    # 76561198326510209,
    # 76561198118726910,
    # 76561198367471798,
    # 76561198019009765,
    # 76561198109083829,
    # 76561198097945516,
    # 76561197971011821,
    # 76561197963534359,
    # 76561198077248235,
    # 76561197981111953,
    # 76561198139084236,
    # 76561198096081579,
    # 76561198045455280,
    # 76561198890581618,
    # 76561198124872187,
    # 76561198093753361,
    # 76561197992133229,
    # 76561198048373585,
    # 76561198152760885,
    # 76561198382166453,
    # 76561198037809069,
    # 76561198005337430,
    # 76561198172367910,
    # 76561198396723427,
    # 76561199168919006,
    # 76561197994616562,
    # 76561199353305847,
    # 76561198006391846,
    # 76561198040421250,
    # 76561197972951657,
    # 76561198044387084,
    # 76561198021180815,
    # 76561197976796589,
    # 76561199080934614,
    # 76561198251835488,
    # 76561198017902347,
    # 76561198102767019,
    # 76561197992548975,
    # 76561198025858988,
    # 76561197993312863,
    # 76561198128158703,
    # 76561198008797636,
    # 76561197965978376,
    # 76561197972378106,
    # 76561198417144062,
    # 76561198015685843,
    # 76561198061393233,
    # 76561198015856631,
    # 76561197983517848,
    # 76561198047438206,
    # 76561197971026489,
    # 76561198318111105,
    # 76561198192399786,
    # 76561198155124847,
    # 76561197982718230,
    # 76561198219343843,
    # 76561198105279930,
    # 76561198039492467,
    # 76561197978640923,
    # 76561198028011423,
    # 76561198996604130,
    # 76561198050474710,
    # 76561199173688191,
    # 76561197984235967,
    # 76561198252374474,
    # 76561198020125851,
    # 76561197988664525,
    # 76561197995008105,
    # 76561198315929726,
    # 76561197973230221,
    # 76561198031837797,
    # 76561197968401807,
    # 76561198034213886,
    # 76561198054210948,
    # 76561198026221141,
    # 76561197997477460,
    # 76561198015992850,
    # 76561197969148931,
    # 76561198025653291,
    # 76561198043532513,
    # 76561198029503957,
    # 76561198045540632,
    # 76561197970246998,
    # 76561198111433283,
    # 76561198096632451,
    # 76561198009596142,
    # 76561198106206019,
    # 76561198018254158,
    # 76561198031164839,
    # 76561198048151962,
    # 76561198004332929,
    # 76561198029532782,
    # 76561197986240493,
    # 76561198294806446,
    # 76561197975329196,
    # 76561198269242105,
    # 76561198104561325,
    # 76561198264362271,
    # 76561198020746864,
    # 76561198046642155,
    # 76561198003041763,
    # 76561198086250077,
    # 76561198025391492,
    # 76561198426000196,
    # 76561198172925593,
    # 76561198154522279,
    # 76561198072936438,
    # 76561197984010356,
    # 76561198042965266,
    # 76561197962630138,
    # 76561197992105918,
    # 76561198120120943,
    # 76561197985091630,
    # 76561198283395702,
    # 76561198042781427,
    # 76561198071709714,
    # 76561198027066612,
    # 76561198124865933,
    # 76561198051725954,
    # 76561198443388781,
    # 76561198171791210,
    # 76561198106145311,
    # 76561198844130640,
    # 76561197981228012,
    # 76561198072361453,
    # 76561198088628817,
    # 76561198032614383,
    # 76561198079227501,
    # 76561197981027062,
    # 76561197991699268,
    # 76561198122276418,
    # 76561198019841907,
    # 76561198015514779,
    # 76561198090111762,
    # 76561197991613008,
    # 76561197970545939,
    # 76561198070220549,
    # 76561198093579202,
    # 76561198074920693,
    # 76561198079896896,
    # 76561198846208086,
    # 76561197973701057,
    # 76561198026306582,
    # 76561197994575642,
    # 76561198085238363,
    # 76561198427572372,
    # 76561197988052802,
    # 76561198028428529,
    # 76561198117483409,
    # 76561198007200913,
    # 76561198150467988,
    # 76561198002535276,
    # 76561198165450871,
    # 76561198101049562,
    # 76561198060520130,
    # 76561197969365800,
    # 76561198008549198,
    # 76561197984605215,
    # 76561198413266831,
    # 76561198413088851,
    # 76561197966617426,
    # 76561198811114019,
    # 76561197977920776,
    # 76561198027668357,
    # 76561197972529138,
    # 76561198004532679,
    # 76561197982273259,
    # 76561198098314980,
    # 76561198119915053,
    # 76561198356842617,
    # 76561198025111129,
    # 76561197970307937,
    # 76561197970970678,
    # 76561197970360549,
    # 76561198083977059,
    # 76561198027917594,
    # 76561197967716198,
    # 76561198831075066,
    # 76561198842603734,
    # 76561198033967307,
    # 76561198408922198,
    # 76561198051740093,
    # 76561198020810038,
    # 76561197998058239,
    # 76561198025834664,
    # 76561197996825541,
    # 76561198217979953,
    # 76561197962850521,
    # 76561197988445370,
    # 76561197994153029
]))

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
