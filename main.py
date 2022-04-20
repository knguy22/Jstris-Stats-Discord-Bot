from ast import alias
import os

import discord
from discord.ext import commands, tasks

import logging

import jstrisfunctions
import jstrishtml
from jstrisfunctions import VersusParameterInit, IndivParameterInit, DateInit, check_user_exists
import cache
from cache import CacheInit

import asyncio
import aiofiles
import json
import random
import statistics

intents = discord.Intents.default()
intents.members = True
description = 'Third party BadgerBot to quickly gather Jstris stats on individual players'
BadgerBot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)

num_processes = 0

lock = asyncio.Lock()

logging.basicConfig(level=logging.INFO, filename="logjstris.log", datefmt='%m/%d/%Y %H:%M:%S',
                    format='%(levelname)s: %(module)s: %(message)s; %(asctime)s')


# GENERAL PURPOSE STUFF
class GeneralMaintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await BadgerBot.change_presence(activity=discord.Game("Jstris, ?help"))
        print(f'Logged in as {BadgerBot.user} (ID: {BadgerBot.user.id})')
        print('------')

    @commands.command()
    async def help(self, ctx) -> None:
        logging.info("Executing help")
        await ctx.send("https://docs.google.com/document/d/"
                       "1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")
        logging.info("Finish help")

    @commands.command()
    async def numprocesses(self, ctx) -> None:
        global num_processes
        await ctx.send(f'{num_processes} processes')

    @staticmethod
    async def num_processes_init(ctx) -> bool:

        """
        Controls the number of processes/CacheInit.fetch_all_games going on at the same time; max processes is 5
        :param ctx:
        :return: bool: option on whether to execute a new CacheInit or not
        """
        global num_processes
        logging.info(f"Checking num processes: {num_processes}")
        num_processes += 1
        if num_processes > 5:
            num_processes -= 1
            logging.info(f"Max processes reached: {num_processes}")
            await ctx.send(ctx.author.mention)
            await ctx.send("Sorry, currently busy handling other requests. Please try again in a few minutes.")
            return False
        logging.info(f"Added one more process: {num_processes}")
        return True

    @staticmethod
    async def num_processes_finish() -> None:
        """
        Subtract num_processes by 1 when a process is finished
        :return:
        """

        global num_processes
        num_processes -= 1
        logging.info(f"Finish process: {num_processes}")

    @commands.command()
    async def prune_user(self, ctx, username) -> None:
        """
        Mainly used for deleting corrupted data; corrupted data in usernames usually comes about when
        keyboard interrupt stops the program while it's making a new stats.json file

        :param ctx:
        :param username:
        :return:
        """
        logging.info('pruning start')
        await cache.prune_user(lock, username)
        await ctx.send(f"Pruned {username}")
        logging.info('pruning done')


# SINGLE PLAYER COMMANDS

class IndivCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['min'])
    async def least(self, ctx, username: str, *args) -> None:

        logging.info("Executing least")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            replay = jstrisfunctions.least_(searched_games.returned_replays, my_ps.param)
            await ctx.send(ctx.author.mention)
            await IndivCommands.replay_send(ctx, replay)

        logging.info("Finish least")

    @commands.command(aliases=['max'])
    async def most(self, ctx, username: str, *args) -> None:
        
        logging.info("Executing most")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            replay = jstrisfunctions.most_(searched_games.returned_replays, my_ps.param)
            await ctx.send(ctx.author.mention)
            await IndivCommands.replay_send(ctx, replay)
        logging.info("Finishing most")

    @commands.command(aliases=['avg', 'indiv'])
    async def average(self, ctx, username: str, *args) -> None:

        my_ps = IndivParameterInit(args)

        if my_ps.game in ('1', '3', '4'):
            data_criteria = ["time", "blocks", "pps", "finesse"]
        elif my_ps.game == '5':
            data_criteria = ["score", "blocks", "ppb", "pps", "finesse"]
        elif my_ps.game == '7':
            data_criteria = ["tsds", "time", "20tsd time", "blocks", "pps"]
        elif my_ps.game == '8':
            data_criteria = ["pcs", "time", "blocks", "pps", "finesse"]
        # Default sprint
        else:
            data_criteria = ["time", "blocks", "pps", "finesse", "date"]

        logging.info("Beginning average")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        await ctx.send(ctx.author.mention)

        if searched_games.has_error:
            await ctx.send(searched_games.error_message)
        else:
            embed = await self.average_indiv_embed(username, data_criteria, searched_games.returned_replays)
            await ctx.send(embed=embed)
        logging.info("Finishing average")

    @commands.command(aliases=['med'])
    async def median(self, ctx, username: str, *args) -> None:

        my_ps = IndivParameterInit(args)

        if my_ps.game in ('1', '3', '4'):
            data_criteria = ["time", "blocks", "pps", "finesse"]
        elif my_ps.game == '5':
            data_criteria = ["score", "blocks", "ppb", "pps", "finesse"]
        elif my_ps.game == '7':
            data_criteria = ["tsds", "time", "20tsd time", "blocks", "pps"]
        elif my_ps.game == '8':
            data_criteria = ["pcs", "time", "blocks", "pps", "finesse"]
        # Default sprint
        else:
            data_criteria = ["time", "blocks", "pps", "finesse", "date"]

        logging.info("Beginning median")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        await ctx.send(ctx.author.mention)

        if searched_games.has_error:
            await ctx.send(searched_games.error_message)
        else:
            embed = await self.median_indiv_embed(username, data_criteria, searched_games.returned_replays)
            await ctx.send(embed=embed)
        logging.info("Finishing median")
    
    @commands.command()
    async def randomindiv(self, ctx, username: str, *args) -> None:
        logging.info("Beginning randomindiv")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()

        searched_games.returned_replays = [i for i in searched_games.returned_replays if i['replay'] != '- ']
        if not searched_games.returned_replays:
            searched_games.has_error = True
            searched_games.error_message = "Error: No available replays links. Replay links have most likely been deleted."

        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            replay = random.choice(searched_games.returned_replays)
            await ctx.send(ctx.author.mention)
            await IndivCommands.replay_send(ctx, replay)
        
        logging.info("Ending randomindiv")

    @commands.command()
    async def indivreplays(self, ctx, username: str, *args) -> None:
        logging.info("Beginning indivreplays")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        
        my_ps = IndivParameterInit(args)
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()

        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            counter = 1
            await ctx.send(ctx.author.mention)
            while searched_games.returned_replays:
                async with aiofiles.open(f'{username}_{counter}.json', 'w') as f:
                    await f.write(json.dumps(searched_games.returned_replays[:20000], indent=1))
                with open(f'{username}_{counter}.json', 'rb') as f:
                    await ctx.send(file=discord.File(f,f'{username}_{counter}.json'))
                os.remove(f'{username}_{counter}.json')
                counter += 1
                searched_games.returned_replays = searched_games.returned_replays[20000:]

    @staticmethod
    async def replay_send(ctx, my_ps: dict) -> None:
        embed = await embed_init(my_ps['username'])

        for i in my_ps:
            if i not in ("username", 'replay'):
                embed.add_field(name=f"**{i}:**", value=my_ps[i], inline=False)
        if my_ps["replay"] != "- ":
            embed.add_field(name="**replay:**", value=my_ps['replay'], inline=False)
        else:
            embed.add_field(name="**replay:**", value="replay not available", inline=False)
        await ctx.send(embed=embed)

        logging.info("Sending replay")

    @staticmethod
    async def average_indiv_embed(username, data_criteria, games):
        embed = await embed_init(username)

        for criteria in data_criteria:
            data_avg = jstrisfunctions.average_(games, criteria)
            embed.add_field(name=f"**{criteria}**", value=str(data_avg), inline=False)

        embed.add_field(name='**games:**', value=str(len(games)), inline=False)

        list_of_dates = list(map(lambda x: jstrisfunctions.DateInit.str_to_datetime(x['date (CET)']), games))
        min_date = jstrisfunctions.DateInit.datetime_to_str_naive(min(list_of_dates))
        max_date = jstrisfunctions.DateInit.datetime_to_str_naive(max(list_of_dates))
        embed.add_field(name='**first date (CET):**', value=min_date, inline=False)
        embed.add_field(name='**last date (CET):**', value=max_date, inline=False)

        return embed
    
    @staticmethod
    async def median_indiv_embed(username, data_criteria, games):
        embed = await embed_init(username)

        for criteria in data_criteria:
            if criteria not in ("time", "20tsd time"):
                games_criteria = [x[criteria] for x in games]
                data_avg = statistics.median(games_criteria)
            else:
                games_criteria = [jstrishtml.clock_to_seconds(x[criteria]) for x in games if x[criteria] != '-']
                data_avg = statistics.median(games_criteria)
                data_avg = jstrishtml.seconds_to_clock(data_avg)
            embed.add_field(name=f"**{criteria}**", value=str(data_avg), inline=False)

        embed.add_field(name='**games:**', value=str(len(games)), inline=False)

        list_of_dates = list(map(lambda x: jstrisfunctions.DateInit.str_to_datetime(x['date (CET)']), games))
        min_date = jstrisfunctions.DateInit.datetime_to_str_naive(min(list_of_dates))
        max_date = jstrisfunctions.DateInit.datetime_to_str_naive(max(list_of_dates))
        embed.add_field(name='**first date (CET):**', value=min_date, inline=False)
        embed.add_field(name='**last date (CET):**', value=max_date, inline=False)

        return embed


# VERSUS COMMANDS

class VsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vs(self, ctx, username: str, *args) -> None:
        logging.info("Beginning vs")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        param_init = VersusParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, param_init, lock)
        await searched_games.fetch_all_games()
        searched_games.returned_replays = searched_games.returned_replays[:param_init.offset]
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None

        # Calculate dates
        list_of_dates = [i['date (CET)'] for i in searched_games.returned_replays]
        dates = await jstrisfunctions.new_first_last_date(list_of_dates)
        first_date = dates[0]
        last_date = dates[1]

        # Calculates averages
        apm_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'apm')
        spm_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'spm')
        pps_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'pps')
        ren_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'ren')
        weight_apm = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'attack') * 60, 2)
        weight_spm = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'sent') * 60, 2)
        weight_pps = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'pcs'), 2)
        time_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'time')
        players_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'players')
        pos_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'pos')
        won_games = jstrisfunctions.games_won(searched_games.returned_replays, param_init.offset)
        games_per_day = round(len(searched_games.returned_replays) / (((jstrisfunctions.DateInit.str_to_datetime(last_date) - jstrisfunctions.DateInit.str_to_datetime(first_date)).days) + 1), 3)

        # Discord formatting
        embed = await embed_init(username)
        embed.add_field(name="**apm:**", value=str(apm_avg), inline=True)
        embed.add_field(name="**spm:**", value=str(spm_avg), inline=True)
        embed.add_field(name="**pps:**", value=str(pps_avg), inline=True)
        embed.add_field(name="**apm (weighted):**", value=str(weight_apm), inline=True)
        embed.add_field(name="**spm (weighted):**", value=str(weight_spm), inline=True)
        embed.add_field(name="**pps (weighted):**", value=str(weight_pps), inline=True)
        embed.add_field(name="**max combo:**", value=str(ren_avg), inline=True)
        embed.add_field(name="**time (seconds):**", value=str(time_avg), inline=True)
        embed.add_field(name="**final position:**", value=str(pos_avg), inline=True)
        embed.add_field(name="**players:**", value=str(players_avg), inline=True)
        embed.add_field(name="**first game (CET):**", value=first_date, inline=True)
        embed.add_field(name="**last game (CET):**", value=last_date, inline=True)
        embed.add_field(name="**games won:**", value=f"{won_games}  "
                                                     f"({won_games / len(searched_games.returned_replays) * 100:.2f}%)",
                        inline=False)
        embed.add_field(name="**number of games:**", value=str(len(searched_games.returned_replays)), inline=False)
        embed.add_field(name="**games per day:**", value=str(games_per_day), inline=False)
        embed.set_footer(text='All of these values are averages. Weighted means weighted by time, not game.')
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)
        logging.info("Finishing vs")
        
    @commands.command(aliases = ['vsmed', 'vs_med'])
    async def vs_median(self, ctx, username: str, *args) -> None:
        logging.info("Beginning vs_median")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        param_init = VersusParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, param_init, lock)
        await searched_games.fetch_all_games()
        searched_games.returned_replays = searched_games.returned_replays[:param_init.offset]
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None

        # Calculate dates
        list_of_dates = [i['date (CET)'] for i in searched_games.returned_replays]
        dates = await jstrisfunctions.new_first_last_date(list_of_dates)
        first_date = dates[0]
        last_date = dates[1]

        # Calculates averages
        apm_med = statistics.median([x['apm'] for x in searched_games.returned_replays])
        spm_med = statistics.median([x['spm'] for x in searched_games.returned_replays])
        pps_med = statistics.median([x['pps'] for x in searched_games.returned_replays])
        ren_med = statistics.median([x['ren'] for x in searched_games.returned_replays])
        time_med = statistics.median([x['time'] for x in searched_games.returned_replays])
        players_med= statistics.median([x['players'] for x in searched_games.returned_replays])
        pos_med = statistics.median([x['pos'] for x in searched_games.returned_replays])
        won_games = jstrisfunctions.games_won(searched_games.returned_replays, param_init.offset)
        games_per_day = round(len(searched_games.returned_replays) / (((jstrisfunctions.DateInit.str_to_datetime(last_date) - jstrisfunctions.DateInit.str_to_datetime(first_date)).days) + 1), 3)

        # Discord formatting
        embed = await embed_init(username)
        embed.add_field(name="**apm:**", value=str(apm_med), inline=True)
        embed.add_field(name="**spm:**", value=str(spm_med), inline=True)
        embed.add_field(name="**pps:**", value=str(pps_med), inline=True)
        embed.add_field(name="**max combo:**", value=str(ren_med), inline=True)
        embed.add_field(name="**time (seconds):**", value=str(time_med), inline=True)
        embed.add_field(name="**final position:**", value=str(pos_med), inline=True)
        embed.add_field(name="**players:**", value=str(players_med), inline=True)
        embed.add_field(name="**first game (CET):**", value=first_date, inline=True)
        embed.add_field(name="**last game (CET):**", value=last_date, inline=True)
        embed.add_field(name="**games won:**", value=f"{won_games}  "
                                                     f"({won_games / len(searched_games.returned_replays) * 100:.2f}%)",
                        inline=False)
        embed.add_field(name="**number of games:**", value=str(len(searched_games.returned_replays)), inline=False)
        embed.add_field(name="**games per day:**", value=str(games_per_day), inline=False)
        embed.set_footer(text='All of these values are medians.')
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)
        logging.info("Finishing vs_median")

    @commands.command()
    async def allmatchups(self, ctx, username: str, *args) -> None:
        logging.info("Beginning allmatchups")
        param_init = VersusParameterInit(args)

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, param_init, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None
        list_of_opponents = await jstrisfunctions.opponents_matchups(searched_games.returned_replays, param_init.offset)

        # Discord formatting stuff

        embed = await embed_init(username)

        c = 0
        for opp, items in list_of_opponents.items():
            if opp is None:
                continue
            winrate = items["won"] / items["games"] * 100
            won_games = items['won']
            embed.add_field(name='**opponent:**', value=f"{c + 1}. {opp}", inline=True)
            embed.add_field(name='**games won (by user):**', value=f"{won_games}  ({winrate:.2f}%)", inline=True)
            embed.add_field(name='**number of games:**', value=items["games"], inline=True)
            c += 1
            if c >= 8:
                break

        num_games = 0
        for opp, items in list_of_opponents.items():
            num_games += items['games']
        embed.add_field(name='total games:', value=str(num_games), inline=False)
        embed.set_footer(text='Only the top 8 players with most played games are shown here For individual match ups '
                              'with more detailed statistics, try using ?indivmatchup instead. Also, Jstris will '
                              'delete replays over time, and they will not be counted here.')

        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)

        logging.info("Finishing allmatchups")

    @commands.command()
    async def vsmatchup(self, ctx, username: str, opponent: str, *args) -> None:
        logging.info("Beginning vsmatchup")
        username = username.lower()
        opponent = opponent.lower()
        param_init = VersusParameterInit(args)

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

        #Check if usernames exist

        if not await jstrisfunctions.check_user_exists(username):
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(f'Not valid username: {username}')
            await GeneralMaintenance.num_processes_finish()
            return None

        if not await jstrisfunctions.check_user_exists(opponent):
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(f'Not valid username: {opponent}')
            await GeneralMaintenance.num_processes_finish()
            return None

        # Username's games
        logging.info(f"Beginning {username}")
        searched_games = CacheInit(username, param_init, lock)
        await searched_games.fetch_all_games()

        if searched_games.has_error:
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            await GeneralMaintenance.num_processes_finish()
            return None
        list_of_opponents = await jstrisfunctions.opponents_matchups(searched_games.returned_replays, param_init.offset)
        embed1 = await VsCommands.vs_matchup_embed(ctx, username, opponent, list_of_opponents)

        # Opponent's games
        logging.info(f"Beginning {opponent}, first: {list_of_opponents[opponent]['min_time']}, "
                     f"last: {list_of_opponents[opponent]['max_time']}")
        searched_games = CacheInit(opponent, param_init, lock)
        await searched_games.fetch_all_games()

        if searched_games.has_error:
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            await GeneralMaintenance.num_processes_finish()
            return None
        list_of_opponents = await jstrisfunctions.opponents_matchups(searched_games.returned_replays, param_init.offset)
        embed2 = await VsCommands.vs_matchup_embed(ctx, opponent, username, list_of_opponents)

        # Finalizing

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()

        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)

        logging.info("Finishing vsmatchup")

    @commands.command()
    async def vsreplays(self, ctx, username: str, *args) -> None:
        logging.info("Beginning indivreplays")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        
        my_ps = VersusParameterInit(args)
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()

        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            counter = 1
            await ctx.send(ctx.author.mention)
            while searched_games.returned_replays:
                async with aiofiles.open(f'{username}_{counter}.json', 'w') as f:
                    await f.write(json.dumps(searched_games.returned_replays[:20000], indent=1))
                with open(f'{username}_{counter}.json', 'rb') as f:
                    await ctx.send(file=discord.File(f,f'{username}_{counter}.json'))
                os.remove(f'{username}_{counter}.json')
                counter += 1
                searched_games.returned_replays = searched_games.returned_replays[20000:]

    @commands.command()
    async def vsmatchupreplays(self, ctx, username: str, opponent: str, *args):
        logging.info("Beginning vsmatchupreplays")
        username = username.lower()
        param_init = VersusParameterInit(args)

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

        # Username's games
        logging.info(f"Beginning {username}")
        searched_games = CacheInit(username, param_init, lock)
        await searched_games.fetch_all_games()

        if searched_games.has_error:
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            await GeneralMaintenance.num_processes_finish()
            return None

        sorted_replays = await jstrisfunctions.opponents_matchups_replays(searched_games.returned_replays)

        if opponent not in sorted_replays:
            await init_message.delete()
            await ctx.send(ctx.author.mention)
            await ctx.send(f'No played games of {username} against {opponent}')
            await GeneralMaintenance.num_processes_finish()
            return None

        list_of_replay_links = []
        for index, replay in enumerate(sorted_replays[opponent]):
            if replay['rep'] and index < param_init.offset:
                list_of_replay_links.append(f"https://jstris.jezevec10.com/replay/1v1/{replay['gid']}?u={username}")

        # You want the oldest replays first if you're recording
        list_of_replay_links.reverse()

        with open('versusmatchupreplays.txt', 'w') as f:
            f.write('localStorage.playReplays = ')
            f.write(str(list_of_replay_links))

        with open("versusmatchupreplays.txt", "rb") as file:
            await init_message.delete()
            await GeneralMaintenance.num_processes_finish()
            await ctx.send(ctx.author.mention)
            await ctx.send(f'Your available replays of {username} vs {opponent} are:', file=discord.File(file, f'{username} vs {opponent}.txt'))

        os.remove("versusmatchupreplays.txt")

    @staticmethod
    async def vs_matchup_embed(ctx, username: str, opponent: str, list_of_opponents: dict) -> [None, discord.Embed]:
        embed = await embed_init(username)

        if opponent in list_of_opponents:
            first_date = list_of_opponents[opponent]["min_time"]
            last_date = list_of_opponents[opponent]["max_time"]
            games_per_day = round(list_of_opponents[opponent]["games"] / ((jstrisfunctions.DateInit.str_to_datetime(last_date) - jstrisfunctions.DateInit.str_to_datetime(first_date)).days + 1), 3)
            winrate = list_of_opponents[opponent]["won"] / list_of_opponents[opponent]["games"] * 100
            won_games = list_of_opponents[opponent]['won']
            has_opponent = True
            embed.add_field(name='**opponent:**', value=opponent, inline=True)
            embed.add_field(name='**games won:**', value=f"{won_games}  ({winrate:.2f}%)", inline=True)
            embed.add_field(name='**total games:**', value=list_of_opponents[opponent]["games"], inline=True)
            embed.add_field(name='**apm:**', value=list_of_opponents[opponent]["apm"], inline=True)
            embed.add_field(name='**spm:**', value=list_of_opponents[opponent]["spm"], inline=True)
            embed.add_field(name='**pps:**', value=list_of_opponents[opponent]["pps"], inline=True)
            embed.add_field(name='**apm (weighted):**', value=list_of_opponents[opponent]["wapm"], inline=True)
            embed.add_field(name='**spm (weighted):**', value=list_of_opponents[opponent]["wspm"], inline=True)
            embed.add_field(name='**pps (weighted):**', value=list_of_opponents[opponent]["wpps"], inline=True)
            embed.add_field(name='**max combo:**', value=list_of_opponents[opponent]["ren"], inline=False)
            embed.add_field(name='**time (seconds):**',
                            value=round(list_of_opponents[opponent]["time_sum"] / list_of_opponents[opponent]['games'], 2),
                            inline=True)
            embed.add_field(name='**Earliest game (CET):**', value=list_of_opponents[opponent]["min_time"], inline=True)
            embed.add_field(name='**Latest game (CET):**', value=list_of_opponents[opponent]["max_time"], inline=True)
            embed.add_field(name='**Games per day:**', value=games_per_day, inline=True)
            embed.set_footer(
                text=' Weighted means weighted by time, not game. Note: Jstris will delete replays over time, '
                     'and they will not be counted here.')
        else:
            has_opponent = False

        if not has_opponent:
            await GeneralMaintenance.num_processes_finish()
            await ctx.send(ctx.author.mention)
            await ctx.send(f"No found games of {username} vs {opponent}.")
            return None

        logging.info("Vsembed init success")

        return embed


# OTHER METHODS

async def embed_init(username: str) -> discord.Embed:
    embed = discord.Embed(
        title=username,
        url=f"https://jstris.jezevec10.com/u/{username}",
        color=discord.Colour.red())
    embed.set_author(name="BadgerBot")
    embed.set_thumbnail(url="https://i.imgur.com/WDUv9f0.png")

    logging.info("Embed init success")
    return embed


@tasks.loop(hours=24)
async def clear_unaccessed_replays() -> None:
    """
    Deletes replays after they haven't been accessed for two weeks

    :return:
    """
    logging.info('pruning start')
    await cache.prune_unused_stats(lock)
    logging.info('pruning done')


@BadgerBot.command()
async def totalgametime(ctx, username: str, first_date='0001-01-01 00:00:01', last_date='9999-01-01 00:00:00') -> None:
    """
    Returns total game time of all indiv and versus modes

    :param ctx:
    :param username:
    :param: first_date:
    :param: last_date:
    :return:
    """
    logging.info("Beginning total_gametime")
    init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

    all_gamemodes = ['sprint20', 'sprint40', 'sprint100', 'sprint1000', 'cheese10', 'cheese18', 'cheese100', 'ultra',
                     'survival', '20tsd', 'pcmode', 'vs']
    await GeneralMaintenance.num_processes_init(ctx)
    total_time = 0
    embed = await embed_init(username)
    dates = DateInit(first_date, last_date)

    if not await jstrisfunctions.check_user_exists(username):
        await init_message.delete()
        await ctx.send(ctx.author.mention)
        await ctx.send(f'Not valid username: {username}')
        await GeneralMaintenance.num_processes_finish()
        return None

    for gamemode in all_gamemodes:

        dates_tuple = (dates.first, dates.last, gamemode)
        if gamemode != 'vs':
            curr_gamemode = CacheInit(username, IndivParameterInit(dates_tuple), lock)
        else:
            curr_gamemode = CacheInit(username, VersusParameterInit(dates_tuple), lock)
        await curr_gamemode.fetch_all_games()

        gamemode_total_time = 0
        for replay in curr_gamemode.returned_replays:
            if gamemode == 'vs':
                gamemode_total_time += float(replay['time'])
            elif gamemode == 'pcmode':
                gamemode_total_time += replay['blocks'] / replay['pps']
            elif gamemode == 'ultra':
                gamemode_total_time += 120
            else:
                gamemode_total_time += jstrishtml.clock_to_seconds(replay['time'])
        embed.add_field(name=f'**{gamemode}:**', value=jstrishtml.seconds_to_timestr(gamemode_total_time), inline=True)

        total_time += gamemode_total_time

    total_time = jstrishtml.seconds_to_timestr(total_time)
    embed.add_field(name=f'**total time:**', value=total_time, inline=True)

    embed.set_footer(text='Units are hours, minutes, and seconds.'
                          'Total time does not count uncompleted replays. Due to how jstris stores replays, only the '
                          'top 200 pcmode and 20tsd replays will be counted.')

    await GeneralMaintenance.num_processes_finish()
    await init_message.delete()
    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)

if __name__ == "__main__":

    if not os.path.exists('playerstats'):
        os.mkdir('playerstats')

    # clear_unaccessed_replays.start()

    BadgerBot.add_cog(GeneralMaintenance(BadgerBot))
    BadgerBot.add_cog(IndivCommands(BadgerBot))
    BadgerBot.add_cog(VsCommands(BadgerBot))

    with open('token.txt', 'r') as r:
        token = r.readline()
        BadgerBot.run(token)
