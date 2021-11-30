import decimal
from collections import OrderedDict

import ijson
import json

import jstrisfunctions
import jstrishtml
import jstrisuser
import os
from decimal import Decimal


def cache_init(username: str, params: [jstrisfunctions.DateInit, jstrisfunctions.IndivParameterInit]) -> list:
    final_stats = []

    if type(params) == jstrisfunctions.DateInit:

        cached_replays_date = fetch_user_vs(username)
        if not cached_replays_date['date']:
            first_date = '0001-01-01 00:00:01'
        else:
            first_date = cached_replays_date['date']
        last_date = '9999-01-01 00:00:00'

        fetched_stats = jstrisuser.UserLiveGames(username, first_date=first_date, last_date=last_date)
        fetched_stats.all_replays = vs_stats_reducer(fetched_stats.all_replays)
        final_stats = cached_replays_date['list'] + fetched_stats.all_replays
        final_stats = duplicate_replay_deleter(final_stats)
        list_of_dates = [i['gtime'] for i in final_stats]
        final_date = jstrisfunctions.new_first_last_date(list_of_dates)[1]

        final_dictionary = {username: {'vs': {'date': final_date, 'list': final_stats}}}
        append_file(username, final_dictionary)

    elif type(params) == jstrisfunctions.IndivParameterInit:

        cached_replays_date = fetch_user_indiv_replays_date(username, params)
        cached_dict = fetch_user_indiv_dict(username, params)
        if not cached_replays_date['date']:
            first_date = '0001-01-01 00:00:01'
        else:
            first_date = cached_replays_date['date']
        last_date = '9999-01-01 00:00:00'

        fetched_stats = jstrisuser.UserIndivGames(username, game=params.game, mode=params.mode,
                                                  first_date=first_date, last_date=last_date)
        final_stats = cached_replays_date['list'] + fetched_stats.all_replays
        final_stats = duplicate_replay_deleter(final_stats)
        list_of_dates = [i['date (CET)'] for i in final_stats]
        final_date = max([jstrisfunctions.DateInit.str_to_datetime(i) for i in list_of_dates])
        final_date = jstrishtml.datetime_to_str_naive(final_date)

        cached_dict[username][params_to_str_key(params)] = {'date': final_date, 'list': final_stats}
        append_file(username, cached_dict)

    return final_stats


def fetch_user_vs(username: str) -> dict:
    with open('stats.json', 'r') as f:
        for player in ijson.items(f, 'item'):
            if username in player.keys():
                return player[username]['vs']

    return {"date": "", "list": []}


def fetch_user_indiv_replays_date(username: str, params: jstrisfunctions.IndivParameterInit) -> dict:

    str_search = params_to_str_key(params)

    with open('stats.json', 'r') as f:
        for player in ijson.items(f, 'item'):
            if username in player.keys():
                if str_search in player[username].keys():
                    return player[username][str_search]

    return {"date": "", "list": []}


def fetch_user_indiv_dict(username: str, params: jstrisfunctions.IndivParameterInit) -> dict:

    str_search = params_to_str_key(params)

    with open('stats.json', 'r') as f:
        for player in ijson.items(f, 'item'):
            if username in player.keys():
                return player

    return {username: {str_search: {'date': '', 'list': []}}}


def append_file(username: str, new_username_stats: dict) -> None:

    with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
        g.write('[')
        try:
            for player in ijson.items(f, 'item'):
                if username in player.keys():
                    continue

                float_player = decimal_to_float(player)
                json.dump(float_player, g, indent=1)
                g.write(',')

        except ijson.common.IncompleteJSONError:
            print('Empty stats.json file')

    with open("new_stats.json", "a") as g:
        float_new_username_stats = decimal_to_float(new_username_stats)
        json.dump(float_new_username_stats, g, indent=1)
        g.write(']')

    os.remove('stats.json')
    os.rename("new_stats.json", 'stats.json')


def params_to_str_key(params: jstrisfunctions.IndivParameterInit) -> str:
    str_search = ""
    if params.game == '1':
        if params.mode == '1':
            str_search = 'sprint40'
        elif params.mode == '2':
            str_search = 'sprint20'
        elif params.mode == '3':
            str_search = 'sprint100'
        elif params.mode == '4':
            str_search = 'sprint1000'
    elif params.game == '3':
        if params.mode == '1':
            str_search = 'cheese10'
        elif params.mode == '2':
            str_search = 'cheese18'
        elif params.mode == '3':
            str_search = 'cheese100'
    elif params.game == '4':
        str_search = 'survival'
    elif params.game == '5':
        str_search = 'ultra'
    elif params.game == '7':
        str_search = '20tsd'
    elif params.game == '8':
        str_search = 'pcmode'

    return str_search


def vs_stats_reducer(all_stats: list) -> list:
    reduced_all_stats = []
    for i in all_stats:
        # i.pop('id')
        # i.pop('gid')
        i.pop('cid')
        # i.pop('rep')
        i.pop('r1v1')
        i.pop('apm')
        i.pop('spm')
        i.pop('pps')
        reduced_all_stats.append(i)

    return all_stats


def duplicate_replay_deleter(my_list: list) -> list:

    frozen_set_list = []
    for i in my_list:
        frozen_set_list.append(frozenset(i.items()))

    ordered_dict_list = OrderedDict.fromkeys(frozen_set_list)
    ordered_dict_list = list(ordered_dict_list)

    new_list = []
    for i in ordered_dict_list:
        new_list.append(dict(i))

    return new_list


def decimal_to_float(my_dict: dict) -> dict:
    for username in my_dict:
        for gamemode in my_dict[username]:
            for gamemode_data in my_dict[username][gamemode]:
                if gamemode_data == "list":
                    for index, replay in enumerate(my_dict[username][gamemode][gamemode_data]):
                        for index2, (stat_key, stat) in enumerate(replay.items()):
                            if type(stat) in (Decimal, decimal.Decimal):
                                replay[stat_key] = round(float(stat), 2)
                        my_dict[username][gamemode][gamemode_data][index] = replay

    return my_dict


if __name__ == "__main__":
    # download_user('dadiumcadmium')
    # open_user()
    # append_file("dadiumcadmium")
    # append_file("sio")

    # cache_init('sio', jstrisfunctions.DateInit('7 months', '1 day'))
    # cache_init('truebulge', jstrisfunctions.IndivParameterInit(('cheese10', 'month')))


    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        cache_init('truebulge', jstrisfunctions.IndivParameterInit(('sprint', 'month')))
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
