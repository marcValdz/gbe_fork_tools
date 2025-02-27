import os

__cold_client_ini = '''
# modified version of ColdClientLoader originally by Rat431
[SteamClient]
# path to game exe, absolute or relative to the loader
Exe={cold_app_exe}
# empty means the folder of the exe
ExeRunDir=
# any additional args to pass, ex: -dx11, also any args passed to the loader will be passed to the app
ExeCommandLine=
# IMPORTANT, unless [Persistence] Mode=2
AppId={cold_appid}

# path to the steamclient dlls, both must be set,
# absolute paths or relative to the loader
SteamClientDll=steamclient.dll
SteamClient64Dll=steamclient64.dll

[Injection]
# force inject steamclient dll instead of waiting for the app to load it
ForceInjectSteamClient=0

# force inject GameOverlayRenderer dll instead of waiting for the app to load it
ForceInjectGameOverlayRenderer=0

# path to a folder containing some dlls to inject into the app upon start, absolute path or relative to this loader
# this folder will be traversed recursively
# additionally, inside this folder you can create a file called `load_order.txt` and
# specify line by line the order of the dlls that have to be injected
# each line should be the relative path of the target dll, relative to the injection folder
# If this file is created then the loader will only inject the .dll files mentioned inside it
# example:
#DllsToInjectFolder=extra_dlls
DllsToInjectFolder=

# don't display an error message when a dll injection fails
IgnoreInjectionError=1
# don't display an error message if the architecture of the loader is different from the app
# this will result in a silent failure if a dll injection didn't succeed
# both the loader and the app must have the same arch for the injection to work
IgnoreLoaderArchDifference=0

[Persistence]
# 0 = turned off
# 1 = loader will spawn the exe and keep hanging in the background until you press "OK"
# 2 = loader will NOT spawn exe, it will just setup the required environemnt and keep hanging in the background
#     you have to run the Exe manually, and finally press "OK" when you've finished playing
#     you have to rename the loader to "steam.exe"
#     it is advised to run the loader as admin in this mode
Mode=0

[Debug]
# don't call `ResumeThread()` on the main thread after spawning the .exe
ResumeByDebugger=0

'''


def generate_cold_client_ini(
    base_out_dir: str,
    appid: int,
    app_exe: str) -> None:

    cold_client_ini_path = os.path.join(base_out_dir, "ColdClientLoader.ini")
    print(f"generating ColdClientLoader.ini in: {cold_client_ini_path}")

    formatted_ini = __cold_client_ini.format(
        cold_app_exe = app_exe,
        cold_appid = appid
    )
    
    with open(cold_client_ini_path, "wt", encoding='utf-8') as f:
        f.writelines(formatted_ini)
