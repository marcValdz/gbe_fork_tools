# GBE Fork - Python-Based Tools

## Overview

This fork introduces several enhancements to improve the functionality, maintainability, and usability of the GBE Tools. Key changes include refactored Python scripts, improved build scripts, better handling of achievements, and automated data retrieval for `top_owner_ids.txt`.

## Features & Improvements

### Code Refactoring & Maintainability

- `generate_emu_config.py` has been refactored into separate files to enhance readability and maintainability.
- Windows build scripts now utilize PowerShell instead of batch scripts.
- The rebuild script now generates full `.exe` files rather than using an `_internal` folder for dependencies.
- Replaced manual flag handling with `argparse`. This should make extensibility much easier.

### Achievement Watcher Integration

- Added support for **Achievement Watcher Playtime Tracking** by running `update_achievement_watcher.exe`.
- All achievement-related processes can be skipped using the `-skip_ach` flag.
- Implemented `difflib`'s similarity algorithm to accurately detect the correct `.exe` for Achievement Watcher.

### Steam Emulator Configuration

- The Codex `steam_emu.ini` generation process now automatically populates `AccountId` and `UserName`:
  - If logged in, it retrieves and fills the correct values.
  - If run with the `-anon` flag, `AccountId` is set to **random** and `UserName` defaults to **Player**.
- It's now possible to skip downloading downloadable content data using the `-skip_dlc` flag.

### Automated Data Retrieval

- `top_owner_ids.txt` is now programmatically generated using the latest data scraped from [**SteamLadder**](https://steamladder.com/ladder/games/).
- The first execution creates the file, and subsequent runs use the existing data unless manually deleted for a fresh scrape.

## Notes

- Executables are now built using [**Nuitka**](https://nuitka.net/), which requires [**Microsoft Visual C++ Build Tools**](https://visualstudio.microsoft.com/visual-cpp-build-tools/). 
- The build scripts are written in a way that it will fetch all possible dependencies even on a compeletely fresh install (at least for Linux).
