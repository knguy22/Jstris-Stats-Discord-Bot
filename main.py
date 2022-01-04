import os

import discord
from discord.ext import commands, tasks

import logging

import jstrisfunctions
import jstrishtml
from jstrisfunctions import VersusParameterInit
from jstrisfunctions import IndivParameterInit

import cache
from cache import CacheInit

import asyncio

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
            a = jstrisfunctions.least_(searched_games.returned_replays, my_ps.param)
            await IndivCommands.replay_send(ctx, a)

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
            a = jstrisfunctions.most_(searched_games.returned_replays, my_ps.param)
            await IndivCommands.replay_send(ctx, a)
        logging.info("Finishing most")

    @commands.command(aliases=['avg'])
    async def average(self, ctx, username: str, *args) -> None:
        logging.info("Beginning average")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        await ctx.send(ctx.author.mention)
        if searched_games.has_error:
            await ctx.send(searched_games.error_message)
        else:
            my_average = jstrisfunctions.average_(searched_games.returned_replays, my_ps.param)
            await ctx.send(f"Average {my_ps.param} for {username} is: {my_average}")
        logging.info("Finishing average")

    @commands.command()
    async def numgames(self, ctx, username: str, *args) -> None:
        logging.info("Beginning numgames")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        await ctx.send(ctx.author.mention)
        if searched_games.has_error:
            await ctx.send(searched_games.error_message)
        else:
            a = len(searched_games.returned_replays)
            await ctx.send(f"{str(a)} games")
        logging.info("Finishing numgames")

    @commands.command()
    async def subblocks(self, ctx, username: str, blocks: str, *args) -> None:
        if not blocks.isdigit():
            await ctx.send(f"Not valid blocks number: {blocks}")
            return None

        logging.info("Beginning sub300")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

        args = list(args)
        args.append('cheese')
        args = tuple(args)

        my_ps = IndivParameterInit(args)
        searched_games = CacheInit(username, my_ps, lock)
        await searched_games.fetch_all_games()

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            a = jstrisfunctions.subblocks(searched_games.returned_replays, int(blocks))
            await ctx.send(ctx.author.mention)
            await ctx.send(f"{username} has {a} sub {blocks}s")
        logging.info("Finishing subblocks")

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
        embed.set_footer(text='Have any suggestions? Please message Truebulge#0358 on Discord!')
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)

        logging.info("Sending replay")


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
        list_of_dates = [i['gtime'] for i in searched_games.returned_replays]
        dates = await jstrisfunctions.new_first_last_date(list_of_dates)
        first_date = dates[0]
        last_date = dates[1]

        # Calculates averages
        apm_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'apm')
        spm_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'spm')
        pps_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'pps')
        weight_apm = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'attack') * 60, 2)
        weight_spm = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'sent') * 60, 2)
        weight_pps = round(jstrisfunctions.live_games_weighted_avg(searched_games.returned_replays, param_init.offset,
                                                                   'pcs'), 2)
        time_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'gametime')
        players_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'players')
        pos_avg = jstrisfunctions.live_games_avg(searched_games.returned_replays, param_init.offset, 'pos')
        won_games = jstrisfunctions.games_won(searched_games.returned_replays, param_init.offset)

        # Discord formatting
        embed = await embed_init(username)
        embed.add_field(name="**apm:**", value=str(apm_avg), inline=True)
        embed.add_field(name="**spm:**", value=str(spm_avg), inline=True)
        embed.add_field(name="**pps:**", value=str(pps_avg), inline=True)
        embed.add_field(name="**apm (weighted):**", value=str(weight_apm), inline=True)
        embed.add_field(name="**spm (weighted):**", value=str(weight_spm), inline=True)
        embed.add_field(name="**pps (weighted):**", value=str(weight_pps), inline=True)
        embed.add_field(name="**time (seconds):**", value=str(time_avg), inline=True)
        embed.add_field(name="**final position:**", value=str(pos_avg), inline=True)
        embed.add_field(name="**players:**", value=str(players_avg), inline=True)
        embed.add_field(name="**first game (CET):**", value=first_date, inline=True)
        embed.add_field(name="**last game (CET):**", value=last_date, inline=True)
        embed.add_field(name="**games won:**", value=f"{won_games}  "
                                                     f"({won_games / len(searched_games.returned_replays) * 100:.2f}%)",
                        inline=False)
        embed.add_field(name="**number of games:**", value=str(len(searched_games.returned_replays)), inline=False)
        embed.set_footer(text='All of these values are averages. Weighted means weighted by time, not game.')
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)
        logging.info("Finishing vs")

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
            embed.add_field(name='**time (seconds):**', value=
                            round(list_of_opponents[opponent]["time_sum"] / list_of_opponents[opponent]['games'], 2),
                            inline=True)
            embed.add_field(name='**Earliest game (CET):**', value=list_of_opponents[opponent]["min_time"], inline=True)
            embed.add_field(name='**Latest game (CET):**', value=list_of_opponents[opponent]["max_time"], inline=True)
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
async def totalgametime(ctx, username: str) -> None:
    """
    Returns total game time of all indiv and versus modes

    :param ctx:
    :param username:
    :return:
    """
    logging.info("Beginning total_gametime")
    init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
    all_gamemodes = ['sprint20', 'sprint40', 'sprint100', 'sprint1000', 'cheese10', 'cheese18', 'cheese100', 'ultra',
                     'survival', '20tsd', 'pcmode', 'vs']
    await GeneralMaintenance.num_processes_init(ctx)
    total_time = 0
    embed = await embed_init(username)

    for gamemode in all_gamemodes:
        if gamemode != 'vs':
            curr_gamemode = CacheInit(username, IndivParameterInit((gamemode, '')), lock)
        else:
            curr_gamemode = CacheInit(username, VersusParameterInit(('0001-01-01 00:00:00', '9999-01-01 00:00:00')), lock)
        await curr_gamemode.fetch_all_games()

        gamemode_total_time = 0
        for replay in curr_gamemode.returned_replays:

            if 'time' in replay.keys():
                gamemode_total_time += jstrishtml.clock_to_seconds(replay['time'])
            elif 'gametime' in replay.keys():
                gamemode_total_time += float(replay['gametime'])
            elif gamemode == 'pcmode':
                gamemode_total_time += replay['blocks'] / replay['pps']
        if gamemode == 'ultra':
            gamemode_total_time += 120 * len(curr_gamemode.returned_replays)

        embed.add_field(name=f'**{gamemode}:**', value=jstrishtml.seconds_to_clock(gamemode_total_time), inline=True)

        total_time += gamemode_total_time

    total_time = jstrishtml.seconds_to_clock(total_time)
    embed.add_field(name=f'**total time:**', value=total_time, inline=True)

    embed.set_footer(text='Total time does not count uncompleted replays. Due to how jstris stores replays, only the '
                          'top 200 pcmode and 20tsd replays will be counted.')

    await GeneralMaintenance.num_processes_finish()
    await init_message.delete()
    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)

if __name__ == "__main__":

    if not os.path.exists('playerstats'):
      os.mkdir('playerstats')

    clear_unaccessed_replays.start()

    BadgerBot.add_cog(GeneralMaintenance(BadgerBot))
    BadgerBot.add_cog(IndivCommands(BadgerBot))
    BadgerBot.add_cog(VsCommands(BadgerBot))

    with open('token.txt', 'r') as r:
        token = r.readline()
        BadgerBot.run(token)
