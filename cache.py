import ijson
import json
import jstrisuser
import os
from decimal import Decimal


def append_file(username):
    new_username_stats = download_user(username)
    new_gamemode = {"date": new_username_stats.last_date_str, "list": new_username_stats.all_stats}
    new_gamemodes = {"vs": new_gamemode}
    new_username = {username: new_gamemodes}

    with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
        g.write('[')
        for player in ijson.items(f, 'item'):
            float_player = decimal_to_float_int(player)
            json.dump(float_player, g, indent=1)
            g.write(',')

    with open("new_stats.json", "a") as f:
        json.dump(new_username, f, indent=1)
        f.write(']')

    os.remove('stats.json')
    os.rename("new_stats.json", 'stats.json')


def download_user(username):
    all_stats = jstrisuser.UserLiveGames(username=username)
    reduced_all_stats = []
    for i in all_stats.all_stats:
        i.pop('id')
        i.pop('gid')
        i.pop('cid')
        i.pop('rep')
        i.pop('apm')
        i.pop('spm')
        i.pop('pps')
        reduced_all_stats.append(i)

    all_stats.all_stats = reduced_all_stats
    return all_stats


def decimal_to_float_int(my_dict):
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
    append_file("truebulge")
    # num_usernames_old_file()


