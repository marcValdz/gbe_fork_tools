# depots.py
import time

def parse_branches(branches: dict) -> list:
    ret = []
    for branch_name, branch_data in branches.items():
        branch_info = {
            'name': branch_name,
            'description': str(branch_data.get("description", "")),
            'protected': False,
            'build_id': 0,  # dummy value
            'time_updated': int(time.time()),  # dummy value
        }
        if 'pwdrequired' in branch_data:
            try:
                protected = str(branch_data["pwdrequired"]).lower()
                branch_info["protected"] = protected in ["true", "1"]
            except Exception:
                pass
        try:
            branch_info["build_id"] = int(branch_data.get("buildid", 0))
        except Exception:
            pass
        if 'timeupdated' in branch_data:
            try:
                branch_info["time_updated"] = int(branch_data["timeupdated"])
            except Exception:
                pass
        ret.append(branch_info)
    return ret

def get_depots_infos(raw_infos):
    try:
        dlc_list = set()
        depot_app_list = set()
        all_depots = set()
        all_branches = []
        try:
            dlc_list = set(map(lambda a: int(str(a).strip()), raw_infos["extended"]["listofdlc"].split(",")))
        except Exception:
            pass
        
        if "depots" in raw_infos:
            depots = raw_infos["depots"]
            for dep, depot_info in depots.items():
                if "dlcappid" in depot_info:
                    dlc_list.add(int(depot_info["dlcappid"]))
                if "depotfromapp" in depot_info:
                    depot_app_list.add(int(depot_info["depotfromapp"]))
                if dep.isnumeric():
                    all_depots.add(int(dep))
                elif str(dep).lower() == 'branches':
                    all_branches.extend(parse_branches(depot_info))
        
        return (dlc_list, depot_app_list, all_depots, all_branches)
    except Exception:
        print("Could not get DLC infos – are there any DLCs?")
        return (set(), set(), set(), [])
