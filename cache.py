import decimal
from decimal import Decimal

from collections import OrderedDict

import ijson
import json

import datetime
import pytz

import jstrisfunctions
import jstrishtml
from jstrisuser import UserLiveGames
from jstrisuser import UserIndivGames
import os

import asyncio
from concurrent.futures import ThreadPoolExecutor

LOOP = asyncio.get_event_loop()


class CacheInit:
    def __init__(self, username: str, params: [jstrisfunctions.DateInit, jstrisfunctions.IndivParameterInit]):
        self.username = username
        self.params = params

        self.gamemode_key = ""
        self.fetched_user_class = []
        self.fetched_replays = []
        self.cached_replays = []
        self.fetched_and_cached_replays = []
        self.returned_replays = []

        self.cached_date = ''
        self.user_dict = {}

        self.has_error = False
        self.error_message = ""

    async def fetch_all_games(self):

        """

        :return: self.returned_replays

        All replays ever filtered out by period; all replays ever are stored into stats.json
        """

        if isinstance(self.params, jstrisfunctions.DateInit):
            self.gamemode_key = 'vs'
        elif isinstance(self.params, jstrisfunctions.IndivParameterInit):
            self.gamemode_key = await self.params_to_str_key(self.params)

        # Versus
        if type(self.params) == jstrisfunctions.DateInit:
            await self.fetch_versus()

        # Indiv gamemodes
        elif type(self.params) == jstrisfunctions.IndivParameterInit:
            await self.fetch_indiv()

    async def fetch_versus(self):
        self.fetch_user()

        if not self.cached_date:
            first_date = '0001-01-01 00:00:01'
        else:
            first_date = self.cached_date
        last_date = '9999-01-01 00:00:00'

        self.fetched_user_class = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                             UserLiveGames, self.username, 1000000000,
                                                             first_date, last_date)
        self.fetched_replays = self.fetched_user_class.all_replays

        await self.vs_reduce_fetched_stats()
        self.fetched_and_cached_replays = self.cached_replays + self.fetched_replays
        self.fetched_and_cached_replays = await self.duplicate_replay_deleter(self.fetched_and_cached_replays)

        if self.fetched_user_class.has_error:
            self.has_error = True
            self.error_message = self.fetched_user_class.error_message
        elif await self.not_has_games(self.fetched_and_cached_replays):
            self.has_error = True
            self.error_message = f"Error: {self.username} has no played games"

        if not self.has_error:
            list_of_dates = [i['gtime'] for i in self.fetched_and_cached_replays]
            for i, j in enumerate(list_of_dates):
                if j is None:
                    print(i, self.fetched_and_cached_replays[i])
            final_date = jstrisfunctions.new_first_last_date(list_of_dates)[1]

            self.user_dict[self.username]['vs'] = {'date': final_date, 'replays': self.fetched_and_cached_replays,
                                                   'date accessed': jstrishtml.datetime_to_str_naive(
                                                       datetime.datetime.now(tz=pytz.timezone('CET')))[:-7]}
            self.append_file(self.user_dict)

            self.returned_replays = await self.vs_period_filter()
            await self.vs_stats_producer()

    async def fetch_indiv(self):
        self.fetch_user()
        if not self.cached_date:
            first_date = '0001-01-01 00:00:01'
        else:
            first_date = self.cached_date
        last_date = '9999-01-01 00:00:00'

        self.fetched_user_class = await LOOP.run_in_executor(ThreadPoolExecutor(), UserIndivGames, self.username,
                                                             self.params.game, self.params.mode, first_date,
                                                             last_date)
        self.fetched_replays = self.fetched_user_class.all_replays
        await self.indiv_reduce_fetched_stats()
        self.fetched_and_cached_replays = self.cached_replays + self.fetched_replays
        self.fetched_and_cached_replays = await self.duplicate_replay_deleter(self.fetched_and_cached_replays)

        if self.fetched_user_class.has_error:
            self.has_error = True
            self.error_message = self.fetched_user_class.error_message
        elif await self.not_has_games(self.fetched_and_cached_replays):
            self.has_error = True
            self.error_message = f"Error: {self.username} has no played games"

        if not self.has_error:
            list_of_dates = [i['date (CET)'] for i in self.fetched_and_cached_replays]
            final_date = max([jstrisfunctions.DateInit.str_to_datetime(i) for i in list_of_dates])
            final_date = jstrishtml.datetime_to_str_naive(final_date)

            self.user_dict[self.username][await self.params_to_str_key(self.params)] = \
                {'date': final_date, 'replays': self.fetched_and_cached_replays,
                 'date accessed': jstrishtml.datetime_to_str_naive(datetime.datetime.now(tz=pytz.timezone('CET')))[:-7]}
            self.append_file(self.user_dict)
            self.returned_replays = await self.indiv_period_filter()
            await self.indiv_stats_producer()

    def fetch_user(self):
        """
        Dictionary containing all gamemodes of user; date of last replay; all replays stored of specific gamemode

        :return: self.user_dict, self.cached_date, self.cached_replays

        """
        self.cached_date = ''
        self.cached_replays = []
        self.user_dict = {self.username: {self.gamemode_key: {'date': '', 'replays': []}}}

        with open('stats.json', 'r') as f:
            for player in ijson.items(f, 'item'):
                if self.username in player.keys():
                    if self.gamemode_key in player[self.username].keys():
                        self.cached_date = self.replace_decimals(player[self.username][self.gamemode_key])
                        self.cached_date = self.cached_date['date']
                        self.cached_replays = self.replace_decimals(player[self.username][self.gamemode_key])
                        self.cached_replays = self.cached_replays['replays']
                    self.user_dict = player

    async def vs_reduce_fetched_stats(self):
        """

        :return: self.fetched_replays: skim off unneeded stats to save memory
        """
        reduced_all_stats = []
        for i in self.fetched_user_class.all_replays:
            i.pop('cid')
            i.pop('r1v1')
            i.pop('apm')
            i.pop('spm')
            i.pop('pps')
            reduced_all_stats.append(i)

        self.fetched_replays = reduced_all_stats

    async def vs_period_filter(self):
        """

        :return: new_list_of_games

        Filtered by first date and last date
        """
        new_list_of_games = []
        games_below_first_date = []
        prev_date = jstrisfunctions.DateInit.str_to_datetime("9999-01-01 00:00:00")

        first_date = jstrisfunctions.DateInit.str_to_datetime(self.params.first)
        last_date = jstrisfunctions.DateInit.str_to_datetime(self.params.last)

        for i, j in enumerate(self.fetched_and_cached_replays):
            curr_date = jstrisfunctions.DateInit.str_to_datetime(j['gtime'])
            if curr_date > last_date:
                pass
            elif first_date < jstrisfunctions.DateInit.str_to_datetime(j['gtime']) < last_date:
                if prev_date > curr_date:
                    new_list_of_games.append(j)
                    prev_date = jstrisfunctions.DateInit.str_to_datetime(new_list_of_games[-1]['gtime'])
                else:
                    new_list_of_games += games_below_first_date
                    games_below_first_date = []
                    new_list_of_games.append(j)
            else:
                games_below_first_date.append(j)

        return new_list_of_games

    async def vs_stats_producer(self):

        """
        Recalculate useful stats like apm, spm, pps

        :return: self.returned_replays
        """
        for i, j in enumerate(self.returned_replays):
            j['apm'] = round(j['attack'] / j['gametime'] * 60, 2)
            j['spm'] = round(j['sent'] / j['gametime'] * 60, 2)
            j['pps'] = round(j['pcs'] / j['gametime'], 2)
            self.returned_replays[i] = j

    async def indiv_reduce_fetched_stats(self):
        """
        Reduces unnecessary statistics/attributes

        :return: self.fetched_replays
        """
        reduced_all_stats = []
        for i in self.fetched_replays:
            i.pop('username')
            reduced_all_stats.append(i)

        self.fetched_replays = reduced_all_stats

    async def indiv_period_filter(self) -> list:
        """
        Filters games by first and last date

        :return: self.fetched_and_cached_replays
        """
        new_list_of_games = []
        first_date = jstrisfunctions.DateInit.str_to_datetime(self.params.first_date)
        last_date = jstrisfunctions.DateInit.str_to_datetime(self.params.last_date)

        for i in self.fetched_and_cached_replays:
            if first_date < jstrisfunctions.DateInit.str_to_datetime(i['date (CET)']) < last_date:
                new_list_of_games.append(i)

        return new_list_of_games

    async def indiv_stats_producer(self):
        """
        Re-adds username to each replay
        :return: self.returned_replays
        """
        for i, j in enumerate(self.returned_replays):
            new_dict = {'username': self.username}
            new_dict.update(j)
            self.returned_replays[i] = new_dict

    def append_file(self, new_username_stats: dict) -> None:
        """
        Parses through old stats.json and appends all other users into new_stats.json.
        Adds new_user at the end

        :param new_username_stats: dictionary of modified user
        :return: stats.json
        """

        with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
            g.write('[')
            try:
                for player in ijson.items(f, 'item'):
                    if self.username in player.keys():
                        continue

                    float_player = self.replace_decimals(player)
                    json.dump(float_player, g, indent=1)
                    g.write(',')

            except ijson.common.IncompleteJSONError:
                print('Empty stats.json file')

        with open("new_stats.json", "a") as g:
            float_new_username_stats = self.replace_decimals(new_username_stats)
            json.dump(float_new_username_stats, g, indent=1)
            g.write(']')

        os.remove('stats.json')
        os.rename("new_stats.json", 'stats.json')

    @staticmethod
    def replace_decimals(obj: dict):
        """
        Replaces objects with Decimal class with floats (this undoes ijson turning all floats into Decimal)

        :param obj: nested dictionary/list
        :return: obj:
        """

        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = CacheInit.replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = CacheInit.replace_decimals(obj[k])
            return obj
        elif isinstance(obj, decimal.Decimal) or isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    @staticmethod
    async def params_to_str_key(params: jstrisfunctions.IndivParameterInit) -> str:
        """
        Assigns gamemode key based on params.game

        :param params: IndivParameterInit
        :return: str_search
        """
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

    @staticmethod
    async def duplicate_replay_deleter(my_list: list) -> list:

        """
        Deletes duplicate replays

        :param my_list: list of replays
        :return: new_list:
        """

        frozen_set_list = []
        for i in my_list:
            frozen_set_list.append(frozenset(i.items()))

        ordered_dict_list = OrderedDict.fromkeys(frozen_set_list)
        ordered_dict_list = list(ordered_dict_list)

        new_list = []
        for i in ordered_dict_list:
            new_list.append(dict(i))

        return new_list

    @staticmethod
    async def not_has_games(my_list: list) -> bool:
        """
        Self explanatory

        :param my_list: list of replays
        :return:
        """
        if len(my_list) > 0:
            return False
        return True

    def __repr__(self):
        """
        Debugging purposes

        :return:
        """
        return f'{self.error_message}'


def check_stats_json_exists():
    """
    Creates stats.json if needed; cache init doesn't work if there isn't at least an empty list inside of the json

    :return:
    """
    if not os.path.exists("stats.json"):
        with open('stats.json', 'w') as f:
            f.write('[]')


def prune_unused_stats():
    """
    Deletes lists of replays who have been last accessed two weeks ago
    :return:
    """
    try:
        with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
            g.write('[')
            for item in ijson.items(f, 'item'):
                for username in item:
                    username_dict = {username: {}}
                    for gamemode in item[username]:
                        for attribute in item[username][gamemode]:
                            if attribute == 'date accessed':
                                if datetime.datetime.now(tz=pytz.timezone('CET'))\
                                        - jstrisfunctions.DateInit.str_to_datetime(item[username][gamemode][attribute]
                                                                                   ) < datetime.timedelta(days=14):
                                    username_dict[username][gamemode] = item[username][gamemode]

                    if username_dict[username]:
                        float_gamemode = CacheInit.replace_decimals(username_dict)
                        json.dump(float_gamemode, g, indent=1)
                        g.write(',')
        with open('new_stats.json', 'rb+') as f:
            f.seek(-1, os.SEEK_END)
            f.truncate()
        with open('new_stats.json', 'a') as f:
            f.write(']')

    except ijson.common.IncompleteJSONError:
        print('Empty stats.json file')

    os.remove('stats.json')
    os.rename("new_stats.json", 'stats.json')


if __name__ == "__main__":
    # async def foo(loop):
    #     game_stats = CacheInit('sio', jstrisfunctions.DateInit('June 25, 2019', 'day'))
    #     await game_stats.fetch_all_games()
    #
    #     dates = jstrisfunctions.opponents_matchups(game_stats.returned_replays)
    #     dates = dates['reminder']
    #     game_stats = CacheInit('reminder', jstrisfunctions.DateInit(dates['min_time'], dates['max_time']))
    #     await game_stats.fetch_all_games()
    #
    #     game_stats = CacheInit('truebulge', jstrisfunctions.IndivParameterInit(('cheese', 'day')))
    #     await game_stats.fetch_all_games()
    #     print(game_stats.returned_replays)
    #
    #     loop.stop()
    #
    #
    # local_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(local_loop)
    # LOOP = asyncio.get_event_loop()
    # asyncio.ensure_future(foo(local_loop))
    # local_loop.run_forever()

    prune_unused_stats()

    # await ggame_Stats.fetch_all_games()

    # k = jstrisfunctions.DateInit('5 months', 'day')
    # j = jstrisuser.UserLiveGames('reminder', first_date=k.first, last_date=k.last)
    # print(j.first_date_str, j.last_date_str)
