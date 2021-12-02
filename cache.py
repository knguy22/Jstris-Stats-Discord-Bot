import decimal
from decimal import Decimal

from collections import OrderedDict

import ijson
import json

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

        self.str_key = ""
        self.fetched_user_class = []
        self.fetched_replays = []
        self.cached_replays = []
        self.all_replays_ever = []
        self.in_period_replays = []

        self.cached_date = ''
        self.cached_dict = {}

        self.has_error = False
        self.error_message = ""

    async def fetch_all_games(self):
        if isinstance(self.params, jstrisfunctions.DateInit):
            self.str_key = 'vs'
        elif isinstance(self.params, jstrisfunctions.IndivParameterInit):
            self.str_key = await self.params_to_str_key(self.params)

        # Versus
        if type(self.params) == jstrisfunctions.DateInit:
            self.fetch_user()

            if not self.cached_date:
                first_date = '0001-01-01 00:00:01'
            else:
                first_date = self.cached_date
            last_date = '9999-01-01 00:00:00'

            self.fetched_user_class = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                                 UserLiveGames, 100000000, first_date, last_date)
            self.fetched_replays = self.fetched_user_class.all_replays
            await self.vs_stats_reducer()
            self.all_replays_ever = self.cached_replays + self.fetched_replays
            self.all_replays_ever = self.duplicate_replay_deleter(self.all_replays_ever)

            if self.fetched_user_class.has_error:
                self.has_error = True
                self.error_message = self.fetched_user_class.error_message
            if self.not_has_games(await self.all_replays_ever):
                self.has_error = True
                self.error_message = f"Error: {self.username} has no played games"

            if not self.has_error:
                list_of_dates = [i['gtime'] for i in await self.all_replays_ever]
                final_date = jstrisfunctions.new_first_last_date(list_of_dates)[1]

                self.cached_dict[self.username]['vs'] = {'date': final_date, 'replays': self.all_replays_ever}
                self.append_file(self.cached_dict)

                self.in_period_replays = await self.vs_period_filter()
                await self.vs_stats_producer()

        # Indiv gamemodes
        elif type(self.params) == jstrisfunctions.IndivParameterInit:

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
            await self.indiv_stats_reducer()
            self.all_replays_ever = self.cached_replays + self.fetched_replays
            self.all_replays_ever = await self.duplicate_replay_deleter(self.all_replays_ever)

            if self.fetched_user_class.has_error:
                self.has_error = True
                self.error_message = self.fetched_user_class.error_message
            if await self.not_has_games(self.all_replays_ever):
                self.has_error = True
                self.error_message = f"Error: {self.username} has no played games"

            if not self.has_error:
                list_of_dates = [i['date (CET)'] for i in self.all_replays_ever]
                final_date = max([jstrisfunctions.DateInit.str_to_datetime(i) for i in list_of_dates])
                final_date = jstrishtml.datetime_to_str_naive(final_date)

                self.cached_dict[self.username][await self.params_to_str_key(self.params)] = \
                    {'date': final_date, 'replays': self.all_replays_ever}
                self.append_file(self.cached_dict)
                self.in_period_replays = await self.indiv_period_filter()
                await self.indiv_stats_producer()

    def fetch_user(self):
        self.cached_date = ''
        self.cached_replays = []
        self.cached_dict = {self.username: {self.str_key: {'date': '', 'replays': []}}}

        with open('stats.json', 'r') as f:
            for player in ijson.items(f, 'item'):
                if self.username in player.keys():
                    if self.str_key in player[self.username].keys():
                        self.cached_date = self.replace_decimals(player[self.username][self.str_key])
                        self.cached_date = self.cached_date['date']
                        self.cached_replays = self.replace_decimals(player[self.username][self.str_key])
                        self.cached_replays = self.cached_replays['replays']
                    self.cached_dict = player

    async def vs_stats_reducer(self):
        reduced_all_stats = []
        for i in self.fetched_user_class.all_stats:
            i.pop('cid')
            i.pop('r1v1')
            i.pop('apm')
            i.pop('spm')
            i.pop('pps')
            reduced_all_stats.append(i)

        self.fetched_replays = reduced_all_stats

    async def vs_period_filter(self):
        new_list_of_games = []
        games_below_first_date = []
        prev_date = jstrisfunctions.DateInit.str_to_datetime("9999-01-01 00:00:00")

        first_date = jstrisfunctions.DateInit.str_to_datetime(self.params.first)
        last_date = jstrisfunctions.DateInit.str_to_datetime(self.params.last)

        for i, j in enumerate(self.all_replays_ever):
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
        for i, j in enumerate(self.in_period_replays):
            j['apm'] = round(j['attack'] / j['gametime'] * 60, 2)
            j['spm'] = round(j['sent'] / j['gametime'] * 60, 2)
            j['pps'] = round(j['pcs'] / j['gametime'], 2)
            self.in_period_replays[i] = j

    async def indiv_stats_reducer(self):
        reduced_all_stats = []
        for i in self.fetched_replays:
            i.pop('username')
            reduced_all_stats.append(i)

        self.fetched_replays = reduced_all_stats

    async def indiv_period_filter(self) -> list:
        new_list_of_games = []
        first_date = jstrisfunctions.DateInit.str_to_datetime(self.params.first_date)
        last_date = jstrisfunctions.DateInit.str_to_datetime(self.params.last_date)

        for i in self.all_replays_ever:
            if first_date < jstrisfunctions.DateInit.str_to_datetime(i['date (CET)']) < last_date:
                new_list_of_games.append(i)

        return new_list_of_games

    async def indiv_stats_producer(self):
        for i, j in enumerate(self.in_period_replays):
            new_dict = {'username': self.username}
            new_dict.update(j)
            self.in_period_replays[i] = new_dict

    def append_file(self, new_username_stats: dict) -> None:

        with open('stats.json', 'r') as f, open('new_stats.json', 'w') as g:
            g.write('[')
            try:
                for player in ijson.items(f, 'item'):
                    if self.username in player.keys():
                        continue

                    float_player = self.replace_decimals(player)
                    json.dump(float_player, g)
                    g.write(',')

            except ijson.common.IncompleteJSONError:
                print('Empty stats.json file')

        with open("new_stats.json", "a") as g:
            float_new_username_stats = self.replace_decimals(new_username_stats)
            json.dump(float_new_username_stats, g)
            g.write(']')

        os.remove('stats.json')
        os.rename("new_stats.json", 'stats.json')

    def replace_decimals(self, obj: dict):
        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = self.replace_decimals(obj[k])
            return obj
        elif isinstance(obj, decimal.Decimal) or isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    @staticmethod
    async def params_to_str_key(params: jstrisfunctions.IndivParameterInit) -> str:
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
        if len(my_list) > 0:
            return False
        return True

    def __repr__(self):
        return f'{self.error_message}'


if __name__ == "__main__":

    ggame_Stats = CacheInit('truebulge', jstrisfunctions.DateInit('June 25, 2021', 'day'))
    # await ggame_Stats.fetch_all_games()

    print(len(ggame_Stats.in_period_replays))
    print(ggame_Stats.in_period_replays[1])

    ggame_Stats = CacheInit('sio', jstrisfunctions.IndivParameterInit(('cheese', 'october 25, 2021', 'day')))
    # await ggame_Stats.fetch_all_games()

    print(ggame_Stats)
    print(len(ggame_Stats.in_period_replays))
    print(ggame_Stats.in_period_replays[1])
    # k = jstrisfunctions.DateInit('5 months', 'day')
    # j = jstrisuser.UserLiveGames('reminder', first_date=k.first, last_date=k.last)
    # print(j.first_date_str, j.last_date_str)
