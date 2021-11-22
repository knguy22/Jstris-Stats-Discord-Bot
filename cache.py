import ijson
import json

import jstrisfunctions
import jstrisuser
import os
from decimal import Decimal


def cache_init(username: str, param_class) -> list:
    if type(param_class) == jstrisfunctions.IndivParameterInit:
        pass
    elif type(param_class) == jstrisfunctions.LiveDateInit:
        pass

    return []


def cache_finish():
    pass


def append_file(username: str) -> None:

    new_username = new_stats(username)

    with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
        g.write('[')
        try:
            for player in ijson.items(f, 'item'):
                float_player = decimal_to_float_int(player)
                json.dump(float_player, g)
                g.write(',')
        except ijson.common.IncompleteJSONError:
            print('Empty stats.json file')

    with open("new_all_replays.json", "a") as g:
        json.dump(new_username, g)
        g.write(']')

    os.remove('all_replays.json')
    os.rename("new_all_replays.json", 'all_replays.json')


def new_stats(username: str) -> dict:
    new_username_stats = download_user(username)
    new_gamemode = {"date": new_username_stats.last_date_str, "list": new_username_stats.all_replays}
    new_gamemodes = {"vs": new_gamemode}
    new_username = {username: new_gamemodes}
    return new_username


def download_user(username: str) -> jstrisuser.UserLiveGames:
    all_stats = jstrisuser.UserLiveGames(username=username)
    reduced_all_stats = []
    for i in all_stats.all_replays:
        # i.pop('id')
        i.pop('gid')
        i.pop('cid')
        # i.pop('rep')
        i.pop('r1v1')
        i.pop('apm')
        i.pop('spm')
        i.pop('pps')
        reduced_all_stats.append(i)

    all_stats.all_replays = reduced_all_stats
    return all_stats


def decimal_to_float_int(my_dict: dict) -> dict:
    for username in my_dict:
        for gamemode in my_dict[username]:
            for replay_list in my_dict[username][gamemode]:
                if replay_list == "list":
                    for index, replay in enumerate(my_dict[username][gamemode][replay_list]):
                        for index2, (stat_key, stat) in enumerate(replay.items()):
                            if type(stat) is Decimal:
                                replay[stat_key] = round(float(stat), 2)
                        my_dict[username][gamemode][replay_list][index] = replay

    return my_dict


if __name__ == "__main__":
    # download_user('dadiumcadmium')
    # open_user()
    append_file("dadiumcadmium")
    append_file("truebulge")
    append_file("sio")
    append_file("vince_hd")
    append_file("quickandsmart")

    # num_usernames_old_file()
