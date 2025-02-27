# GBE Fork - Python-Based Tools

## Overview

This fork introduces several enhancements to improve the functionality, maintainability, and usability of the GBE project. Key changes include refactored Python scripts, improved Windows build scripts, better handling of achievements, and automated data retrieval for `top_owner_ids.txt`.

## Features & Improvements

### Code Refactoring & Maintainability

- `generate_emu_`[`config.py`](http://config.py "Linkify Plus Plus") has been refactored into separate files to enhance readability and maintainability.
- Windows build scripts now utilize PowerShell instead of batch scripts.
- The rebuild script now generates full `.exe` files rather than using an `_internal` folder for dependencies.

### Achievement Watcher Integration

- Added support for **Achievement Watcher Playtime Tracking** by running `update_achievement_watcher.exe`.
- All achievement-related processes can be skipped using the `-skip_ach` argument.
- Implemented `difflib`'s similarity algorithm to accurately detect the correct `.exe` for Achievement Watcher.

### Steam Emulator Configuration

- The Codex `steam_emu.ini` generation process now automatically populates `AccountId` and `UserName`:
  - If logged in, it retrieves and fills the correct values.
  - If run with the `-anon` argument, `AccountId` is set to **random** and `UserName` defaults to **Player**.

### Automated Data Retrieval

- `top_owner_ids.txt` is now programmatically generated using the latest scraped data from [**SteamLadder**](https://steamladder.com/ladder/games/).
- The first execution creates the file, and subsequent runs use the existing data unless manually deleted for a fresh scrape.

## Notes

- This project was developed with the assistance of ChatGPT's reasoning model.
- While major features have been tested, extensive testing of all refactored components is still pending.
- Linux scripts have not yet been updated, as [**Achievement Watcher**](https://github.com/xan105/Achievement-Watcher) is Windows-only.
