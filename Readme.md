## Python Based Tools for GBE Fork
This fork tries to add a couple new features:
- The `generate_emu_config.py` has been refactored to separate files to improve readability and maintainability.
- The windows build scripts have been updated to use Powershell.
- The rebuild script is now asked to create full .exe files instead of having a separate _internal folder that contains dependencies.
- Support for **Achivement Watcher Playtime Tracking** by running `update_achievement_watcher.exe`.
- Everthing related to achievements can now be skipped using the argument: _-skip_ach_
- Utilized difflib's similarity algorithm to properly detect the correct .exe to be used for Achievement Watcher.
- The codex steam_emu.ini generation now automatically fills `AccountId` and `UserName` with the correct values when logged-in. `AccountId` is set to **random** and `UserName` is set to **Player** when ran with the _-anon_ argument.
- The `top_owner_ids.txt` file is now programatically filled with the latest scraped data from [SteamLadder](https://steamladder.com/ladder/games/). The first run will create the file, and any subsequent runs will utilize it until the user decides to delete it if they wish to rescrape again.

NOTE: This was made with the assistance of ChatGPT's reasoning model. I haven't extensively tested every single aspect of the script after refactoring, but the major features seem to be working fine.
