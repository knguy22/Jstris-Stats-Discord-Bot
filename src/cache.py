import json

import datetime
from typing import Union
import pytz

import jstrisfunctions
from jstrisfunctions import DateInit

from jstrisuser import UserLiveGames
from jstrisuser import UserIndivGames
import os

import logging
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, filename="logjstris.log", datefmt='%m/%d/%Y %H:%M:%S',
                    format='%(levelname)s: %(module)s: %(message)s; %(asctime)s')

class CacheInit:
    def __init__(self, username: str, params: Union[jstrisfunctions.VersusParameterInit, jstrisfunctions.IndivParameterInit],
                 lock: asyncio.Lock):
        self.username = username.lower()
        self.params = params
        self.lock = lock

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
        
        if not os.path.exists("playerstats"):
            os.mkdir("playerstats")
            
        # Gamemode key tells which replays to check (ie cheese or vs or ultra)
        if isinstance(self.params, jstrisfunctions.VersusParameterInit):
            self.gamemode_key = 'vs'
        elif isinstance(self.params, jstrisfunctions.IndivParameterInit):
            self.gamemode_key = self.params_to_str_key(self.params)

    async def fetch_all_games(self) -> None:

        """
        :return: self.returned_replays
        All replays ever filtered out by period; all replays ever are stored into stats.json
        """

        # Gamemode key tells which replays to check (ie cheese or vs or ultra)
        if isinstance(self.params, jstrisfunctions.VersusParameterInit):
            self.gamemode_key = 'vs'
        elif isinstance(self.params, jstrisfunctions.IndivParameterInit):
            self.gamemode_key = self.params_to_str_key(self.params)

        logging.info(self.params)
        logging.info(self.gamemode_key)

        if self.params.has_error:
            self.has_error = True
            self.error_message = self.params.error_message
            return None

        # Choose which gamemode or replays you want to fetch
        if type(self.params) == jstrisfunctions.VersusParameterInit:
            await self.fetch_versus_replays()
        elif type(self.params) == jstrisfunctions.IndivParameterInit:
            await self.fetch_indiv_replays()
        else:
            self.has_error = True
            self.error_message = f'Not valid param type: {self.params}, {type(self.params)}'
        
        for i in self.params.comparisons:
            await self.filter_using_sorting_criteria(i)
        await self.filter_using_has_links(self.params.has_links)

        # Final check if replays are empty
        if await self.not_has_games(self.returned_replays) and not self.has_error:
            self.has_error = True
            self.error_message = f"Error: {self.username} has no played games"

    async def fetch_versus_replays(self) -> None:
        """
        Fetches versus replays, stored in cache and not yet stored in cache
        :return:
        """
        await self.fetch_replays_from_cache()

        if not self.cached_date:
            first_date = '0001-01-01 00:00:01'
        else:
            first_date = self.cached_date
        last_date = '9999-01-01 00:00:00'

        # Gathers uncached replays from jstris
        LOOP = asyncio.get_event_loop()
        self.fetched_user_class = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                             UserLiveGames, self.username, 100000000000,
                                                             first_date, last_date)
        self.fetched_replays = self.fetched_user_class.all_replays

        # Processes replays; note: fetched_replays must be added before cached_replays in order to maintain proper
        # date ordering
        await self.reduce_fetched_replays_vs()
        self.fetched_and_cached_replays = self.fetched_replays + self.cached_replays
        self.fetched_and_cached_replays = await self.duplicate_replay_deleter(self.fetched_and_cached_replays)
        await self.rename_replays_stats_vs()

        # Checks for problems or errors with all replays
        if self.fetched_user_class.has_error:
            self.has_error = True
            self.error_message = self.fetched_user_class.error_message
        elif await self.not_has_games(self.fetched_and_cached_replays):
            self.has_error = True
            self.error_message = f"Error: {self.username} has no played games"

        if not self.has_error:
            list_of_dates = [i['date (CET)'] for i in self.fetched_and_cached_replays]
            final_date = await jstrisfunctions.new_first_last_date(list_of_dates)

            # Checks if the versus filter could not find a first or last date
            if not final_date:
                self.has_error = True
                self.error_message = f"Error: {self.username} has no valid games"
                return None

            # Stores all replays into the cache
            final_date = final_date[1]
            self.user_dict['vs'] = {'date': final_date, 'replays': self.fetched_and_cached_replays,
                                                   'date accessed': DateInit.datetime_to_str_naive(
                                                       datetime.datetime.now(tz=pytz.timezone('CET')))[:-7]}
            await self.store_player_stats(self.user_dict)

            # Returns fetched replays
            self.returned_replays = await self.filter_period_vs()
            await self.produce_vs_stats()

    async def fetch_indiv_replays(self) -> None:
        """
        Fetches single player replays, stored in cache or not yet stored in cache
        :return:
        """
        
        final_date = DateInit.datetime_to_str_naive(datetime.datetime.now(tz=pytz.timezone('CET')))[:-7]
        
        # await self.fetch_replays_from_cache()

        # if not self.cached_date:
        #     first_date = '0001-01-01 00:00:01'
        # else:
        #     first_date = self.cached_date
        first_date = '0001-01-01 00:00:01'
        last_date = '9999-01-01 00:00:00'

        # Gathers uncached replays from jstris
        LOOP = asyncio.get_event_loop()
        self.fetched_user_class = await LOOP.run_in_executor(ThreadPoolExecutor(), UserIndivGames, self.username,
                                                             self.params.game, self.params.mode, first_date,
                                                             last_date)
        self.fetched_replays = self.fetched_user_class.all_replays

        # Processes requested replays and merges with cached replays
        await self.reduced_fetched_replays_indiv()
        self.fetched_and_cached_replays = self.cached_replays + self.fetched_replays
        self.fetched_and_cached_replays = await self.duplicate_replay_deleter(self.fetched_and_cached_replays)

        # Checks for problems and errors
        if self.fetched_user_class.has_error:
            self.has_error = True
            self.error_message = self.fetched_user_class.error_message
        elif await self.not_has_games(self.fetched_and_cached_replays):
            self.has_error = True
            self.error_message = f"Error: {self.username} has no played games"

        # Stores all replays into cache
        if not self.has_error:

            # self.user_dict[self.gamemode_key] = \
            #     {'date': final_date, 'replays': self.fetched_and_cached_replays,
            #      'date accessed': final_date}
            # await self.store_player_stats(self.user_dict)

            # Returns replays
            self.returned_replays = await self.filter_period_indiv()
            await self.produce_indiv_stats()

    async def fetch_replays_from_cache(self) -> None:
        """
        Dictionary containing all gamemodes of user; date of last replay; all replays stored of specific gamemode
        :return: self.user_dict, self.cached_date, self.cached_replays
        """

        # Initializes json later when replays are stored back into cache
        self.cached_date = ''
        self.cached_replays = []
        self.user_dict = {self.gamemode_key: {'date': '', 'replays': []}}

        logger.info(f'Beginning fetching {self.username}')

        # Grabs desired gamemode replays from {username}.json
        async with self.lock:
            if os.path.exists(f"playerstats/{self.username}.json"):
                async with aiofiles.open(f"playerstats/{self.username}.json", 'r') as f:
                    player_stats = json.loads(await f.read())
                    self.user_dict = player_stats
        logger.info(f'Ending fetching {self.username}')

        # Processes fetched replays
        self.user_dict = await self.replace_decimals(self.user_dict)
        if self.gamemode_key in self.user_dict.keys():
            self.cached_date = self.user_dict[self.gamemode_key]['date']
            self.cached_replays = self.user_dict[self.gamemode_key]['replays']

    async def reduce_fetched_replays_vs(self) -> None:
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

    async def rename_replays_stats_vs(self) -> None:
        for i in self.fetched_and_cached_replays:
            if 'gametime' in i:
                i['time'] = i['gametime']
                i.pop('gametime')
            if 'gtime' in i:
                i['date (CET)'] = i['gtime']
                i.pop('gtime')
                
    async def filter_period_vs(self) -> list:
        """
        :return: new_list_of_games
        Filtered by first date and last date
        """
        new_list_of_games = []
        games_below_first_date = []
        prev_date = jstrisfunctions.DateInit.str_to_datetime("9999-01-01 00:00:00")

        first_date = jstrisfunctions.DateInit.str_to_datetime(self.params.first_date)
        last_date = jstrisfunctions.DateInit.str_to_datetime(self.params.last_date)

        # Jstris will sometimes store versus replays with the wrong dates, which causes issues when trying to find
        # versus replays in a specific time period. Since jstris most often stores replays with a date wrongly far off
        # into the past, there being a replay whose date is above the earliest date of a given time period will return
        # all replays with game ID above (or stored after) that first replay because it is not likely that the replay's
        # true date is later than the stored replay's date

        for i, j in enumerate(self.fetched_and_cached_replays):
            curr_date = jstrisfunctions.DateInit.str_to_datetime(j['date (CET)'])
            if curr_date > last_date:
                pass
            elif first_date < jstrisfunctions.DateInit.str_to_datetime(j['date (CET)']) < last_date:
                if prev_date > curr_date:
                    new_list_of_games.append(j)
                    prev_date = jstrisfunctions.DateInit.str_to_datetime(new_list_of_games[-1]['date (CET)'])
                else:
                    new_list_of_games += games_below_first_date
                    games_below_first_date = []
                    new_list_of_games.append(j)
            else:
                games_below_first_date.append(j)

        return new_list_of_games

    async def produce_vs_stats(self) -> None:

        """
        Recalculate useful stats like apm, spm, pps
        :return: self.returned_replays
        """
        for i, j in enumerate(self.returned_replays):
            j['apm'] = round(j['attack'] / j['time'] * 60, 2)
            j['spm'] = round(j['sent'] / j['time'] * 60, 2)
            j['pps'] = round(j['pcs'] / j['time'], 2)
            self.returned_replays[i] = j

    async def reduced_fetched_replays_indiv(self) -> None:
        """
        Reduces unnecessary statistics/attributes
        :return: self.fetched_replays
        """
        reduced_all_stats = []
        for i in self.fetched_replays:
            i.pop('username')
            reduced_all_stats.append(i)

        self.fetched_replays = reduced_all_stats

    async def filter_period_indiv(self) -> list:
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

    async def produce_indiv_stats(self) -> None:
        """
        Re-adds username to each replay
        :return: self.returned_replays
        """
        for i, j in enumerate(self.returned_replays):
            new_dict = {'username': self.username}
            new_dict.update(j)
            self.returned_replays[i] = new_dict

    async def store_player_stats(self, new_username_stats: dict) -> None:
        logger.info(f'Starting storing {self.username} stats {self.username}')

        async with aiofiles.open(f"playerstats/{self.username}.json", 'w') as f:
            float_new_username_stats = await self.replace_decimals(new_username_stats)
            await f.write(json.dumps(float_new_username_stats))

        logger.info(f'Ending storing {self.username} stats {self.username}')

    async def filter_using_sorting_criteria(self, comparison_dict):
        # param = self.params.comparison_param
        # operator = self.params.comparison_operator
        # value = self.params.comparison_value
        param = comparison_dict['param']
        operator = comparison_dict['operator']
        value = comparison_dict['value']
        replays = self.returned_replays
        if not operator:
            return None

        if param == 'date (CET)':
            for i, j in enumerate(self.returned_replays):
                self.returned_replays[i][param] = DateInit.str_to_datetime(j[param])
        elif param == 'time':
            for i, j in enumerate(self.returned_replays):
                if type(self.params) == jstrisfunctions.VersusParameterInit:
                    self.returned_replays[i][param] = j[param]
                elif type(self.params) == jstrisfunctions.IndivParameterInit:
                    self.returned_replays[i][param] = jstrisfunctions.DateInit.clock_to_seconds(j[param])

        filtered_replays = []
        for i in replays:
            exec_bool = False
            if operator == '<=' and i[param] <= value:
                exec_bool = True
            elif operator == '>=' and i[param] >= value:
                exec_bool = True
            elif operator == '==' and i[param] == value:
                exec_bool = True
            elif operator == '<' and i[param] < value:
                exec_bool = True
            elif operator == '>' and i[param] > value:
                exec_bool = True
            if exec_bool:
                filtered_replays.append(i)
        self.returned_replays = filtered_replays

        if param == 'date (CET)':
            for i, j in enumerate(self.returned_replays):
                self.returned_replays[i][param] = DateInit.datetime_to_str_naive(j[param])
        elif param == 'time':
            if type(self.params) == jstrisfunctions.IndivParameterInit:
                for i, j in enumerate(self.returned_replays):
                    self.returned_replays[i][param] = jstrisfunctions.DateInit.seconds_to_clock(j[param])
                    
    async def filter_using_has_links(self, has_links):
        if has_links == None:
            return
        elif has_links == True:
            self.returned_replays = [i for i in self.returned_replays if i['replay'] not in ('- ', '-')]
        elif has_links == False:
            self.returned_replays = [i for i in self.returned_replays if i['replay'] in ('- ', '-')]

    @staticmethod
    async def replace_decimals(obj):
        """
        Replaces objects with Decimal class with floats (this undoes ijson turning all floats into Decimal)
        :param obj: nested dictionary/list
        :return: obj:
        """

        if isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = await CacheInit.replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = await CacheInit.replace_decimals(obj[k])
            return obj
        # Replaces decimal type without replacing ints or strs
        try:
            if obj is None or type(obj) in (int, str):
                raise ValueError
            return float(obj)
        except ValueError:
            return obj

    @staticmethod
    def params_to_str_key(params: jstrisfunctions.IndivParameterInit) -> str:
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
        
        new_list = {str(i): i for i in my_list}
        new_list = [i for i in new_list.values()]

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


async def prune_unused_stats(lock: asyncio.Lock) -> None:
    """
    Gets rid of gamemode stats that have not been accessed within the last two weeks

    :param lock: asyncio.Lock
    :return:
    """
    async with lock:
        list_of_filenames = os.listdir('playerstats')
        for file in list_of_filenames:
            new_player_stats = {}

            # Checks each gamemode's dates and stores acceptable gamemode stats to new_player_stats
            async with aiofiles.open(f'playerstats/{file}', 'r') as f:
                # async for player_stats in ijson.items_async(f, ''):
                player_stats = json.loads(await f.read())
                for gamemode in player_stats:
                    gamemode_date = player_stats[gamemode]['date accessed']
                    if datetime.datetime.now(tz=pytz.timezone('CET')) - jstrisfunctions.DateInit.str_to_datetime(gamemode_date) < datetime.timedelta(days=14):
                        new_player_stats[gamemode] = player_stats[gamemode]

            # Writes new_player_stats
            async with aiofiles.open(f'playerstats/{file}', 'w') as f:
                new_player_stats = await CacheInit.replace_decimals(new_player_stats)
                await f.write(json.dumps(new_player_stats))


async def prune_user(lock: asyncio.Lock, prune_username: str) -> None:
    """
    Removes a player from the database
    :param lock: asyncio.Lock
    :param prune_username: str
    :return:
    """
    username = prune_username.lower()
    async with lock:
        if os.path.exists(f'playerstats/{username}.json'):
            os.remove(f'playerstats/{username}.json')

if __name__ == "__main__":
    pass

