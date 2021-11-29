import discord
from discord.ext import commands
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import jstrisfunctions
from jstrisfunctions import DateInit
from jstrisfunctions import IndivParameterInit
from jstrisuser import UserIndivGames
from jstrisuser import UserLiveGames


intents = discord.Intents.default()
intents.members = True
description = 'Third party BadgerBot to quickly gather Jstris stats on individual players'
BadgerBot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)

LOOP = asyncio.get_event_loop()
num_processes = 0

logging.basicConfig(level=logging.INFO, filename="logjstris.log", datefmt='%m/%d/%Y %H:%M:%S',
                    format='%(levelname)s: %(module)s: %(message)s; %(asctime)s')


# GENERAL PURPOSE STUFF
class GeneralMaintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {BadgerBot.user} (ID: {BadgerBot.user.id})')
        print('------')

    @commands.command()
    async def help(self, ctx):
        logging.info("Executing help")
        await ctx.send("https://docs.google.com/document/d/"
                       "1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")
        logging.info("Finish help")

    @staticmethod
    async def num_processes_init(ctx) -> bool:
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
    async def num_processes_finish():
        global num_processes
        num_processes -= 1
        logging.info(f"Finish process: {num_processes}")


# SINGLE PLAYER COMMANDS

class IndivCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def least(self, ctx, username: str, *args):
        logging.info("Executing least")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserIndivGames,
                                                    username, my_ps.game, my_ps.mode, my_ps.first_date, my_ps.last_date)
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            a = jstrisfunctions.least_(searched_games.all_replays, my_ps.param)
            await IndivCommands.replay_send(ctx, a)

        logging.info("Finish least")

    @commands.command()
    async def most(self, ctx, username: str, *args):
        logging.info("Executing most")

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserIndivGames,
                                                    username, my_ps.game, my_ps.mode, my_ps.first_date, my_ps.last_date)
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            a = jstrisfunctions.most_(searched_games.all_replays, my_ps.param)
            await IndivCommands.replay_send(ctx, a)
        logging.info("Finishing most")

    @commands.command()
    async def average(self, ctx, username: str, *args):
        logging.info("Beginning average")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserIndivGames,
                                                    username, my_ps.game, my_ps.mode, my_ps.first_date, my_ps.last_date)
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            my_average = jstrisfunctions.average_(searched_games.all_replays, my_ps.param)
            await ctx.send(f"Average {my_ps.param} for {username} is: {my_average}")
        logging.info("Finishing average")

    @commands.command()
    async def numgames(self, ctx, username: str, *args):
        logging.info("Beginning numgames")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        my_ps = IndivParameterInit(args)
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserIndivGames,
                                                    username, my_ps.game, my_ps.mode, my_ps.first_date, my_ps.last_date)
        await GeneralMaintenance.num_processes_finish()

        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            a = len(searched_games.all_replays)
            await ctx.send(f"{str(a)} games")
        logging.info("Finishing numgames")

    @commands.command()
    async def sub300(self, ctx, username: str, *args):
        logging.info("Beginning sub300")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

        my_ps = IndivParameterInit(args)
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserIndivGames,
                                                    username, "3", "3", my_ps.first_date, my_ps.last_date)
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
        else:
            a = jstrisfunctions.sub300(searched_games.all_replays)
            await ctx.send(ctx.author.mention)
            await ctx.send(f"{username} has {a} sub 300s")
        logging.info("Finishing sub300")

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
    async def vs(self, ctx, username: str, offset: int = 10):
        logging.info("Beginning vs")
        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserLiveGames,
                                                    username, offset)
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None

        # Calculates averages
        apm_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'apm')
        spm_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'spm')
        pps_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'pps')
        weight_apm = round(jstrisfunctions.live_games_weighted_avg(searched_games.all_replays, offset, 'attack') * 60,
                           2)
        weight_spm = round(jstrisfunctions.live_games_weighted_avg(searched_games.all_replays, offset, 'sent') * 60, 2)
        weight_pps = round(jstrisfunctions.live_games_weighted_avg(searched_games.all_replays, offset, 'pcs'), 2)
        time_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'gametime')
        players_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'players')
        pos_avg = jstrisfunctions.live_games_avg(searched_games.all_replays, offset, 'pos')
        won_games = jstrisfunctions.games_won(searched_games.all_replays, offset)

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
        embed.add_field(name="**games won:**", value=f"{won_games}  "
                                                     f"({won_games / len(searched_games.all_replays) * 100:.2f}%)",
                        inline=False)
        embed.add_field(name="**number of games:**", value=str(len(searched_games.all_replays)), inline=False)
        embed.set_footer(text='All of these values are averages. Weighted means weighted by time, not game.')
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed)
        logging.info("Finishing vs")

    @commands.command()
    async def allmatchups(self, ctx, username: str, first_date: str = "1000 months", last_date: str = "0 days"):
        logging.info("Beginning allmatchups")
        date_init = DateInit(first_date, last_date)
        if date_init.has_error:
            await ctx.send(date_init.error_message)
            return 0

        first_date = date_init.first
        last_date = date_init.last

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None

        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserLiveGames,
                                                    username, 1000000000, first_date, last_date)
        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None
        list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_replays)

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
    async def vsmatchup(self, ctx, username: str, opponent: str, first_date: str = "1000 months",
                        last_date: str = "0 days"):
        logging.info("Beginning vsmatchup")
        username = username.lower()
        opponent = opponent.lower()
        date_init = DateInit(first_date, last_date)
        if date_init.has_error:
            await ctx.send(date_init.error_message)
            return 0

        first_date = date_init.first
        last_date = date_init.last

        if not await GeneralMaintenance.num_processes_init(ctx):
            return None
        init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")

        # Username's games
        logging.info(f"Beginning {username}")
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserLiveGames,
                                                    username, 10000000000, first_date, last_date)

        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None
        list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_replays)
        embed1 = await VsCommands.vs_matchup_embed(ctx, username, opponent, list_of_opponents)

        # Opponent's games
        logging.info(f"Beginning {opponent}, first: {list_of_opponents[opponent]['min_time']}, "
                     f"last: {list_of_opponents[opponent]['max_time']}")
        opp_first_date = list_of_opponents[opponent]["min_time"]
        opp_last_date = list_of_opponents[opponent]["max_time"]
        searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
                                                    UserLiveGames,
                                                    opponent, 10000000, opp_first_date, opp_last_date)
        if searched_games.has_error:
            await ctx.send(ctx.author.mention)
            await ctx.send(searched_games.error_message)
            return None
        list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_replays)
        embed2 = await VsCommands.vs_matchup_embed(ctx, opponent, username, list_of_opponents)

        # Finalizing

        await GeneralMaintenance.num_processes_finish()
        await init_message.delete()

        await ctx.send(ctx.author.mention)
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)

        logging.info("Finishing vsmatchup")

    # @commands.command()
    # async def vsprogress(self, ctx, username: str, first_date: str = "1000 months", last_date: str = "0 days"):
    #     logging.info("Beginning allmatchups")
    #     date_init = DateInit(first_date, last_date)
    #     if date_init.has_error:
    #         await ctx.send(date_init.error_message)
    #         return 0
    #
    #     first_date = date_init.first
    #     last_date = date_init.last
    #
    #     if not await GeneralMaintenance.num_processes_init(ctx):
    #         return None
    #
    #     init_message = await ctx.send(f"Searching {username}'s games now. This can take a while.")
    #     searched_games = await LOOP.run_in_executor(ThreadPoolExecutor(),
    #                                                 UserLiveGames,
    #                                                 username, 1000000000, first_date, last_date)
    #     await GeneralMaintenance.num_processes_finish()
    #     await init_message.delete()
    #     if searched_games.has_error:
    #         await ctx.send(ctx.author.mention)
    #         await ctx.send(searched_games.error_message)
    #         return None
    #
    #     all_games = searched_games.all_replays
    #     list_of_times = [datetime.datetime.strptime(game['gtime'], "%Y-%m-%d %H:%M:%S") for game in all_games]
    #     list_of_apms = [game['apm'] for game in all_games]
    #     list_of_sizes = [5 for game in list_of_times]
    #
    #     plt.xlabel('Date')
    #     plt.ylabel('Apm')
    #     plt.title(f'{username}: Apm Over Time')
    #     plt.ylim(top=150)
    #     plt.scatter(list_of_times, list_of_apms, list_of_sizes)
    #     plt.savefig('saved_figure.png')
    #     with open('saved_figure.png', "rb") as fh:
    #         f = discord.File(fh, filename='saved_figure.png')
    #
    #     await ctx.send(file=f)
    #     plt.clf()

    @staticmethod
    async def vs_matchup_embed(ctx, username: str, opponent: str, list_of_opponents: dict):
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
            embed.add_field(name='**Earliest game (CET):**', value=list_of_opponents[opponent]["min_time"], inline=True)
            embed.add_field(name='**Latest game (CET):**', value=list_of_opponents[opponent]["max_time"], inline=True)
            embed.set_footer(
                text=' Weighted means weighted by time, not game. Note: Jstris will delete replays over time, '
                     'and they will not be counted here.')
        else:
            has_opponent = False

        if not has_opponent:
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


if __name__ == "__main__":

    # Token
    BadgerBot.add_cog(GeneralMaintenance(BadgerBot))
    BadgerBot.add_cog(IndivCommands(BadgerBot))
    BadgerBot.add_cog(VsCommands(BadgerBot))
    BadgerBot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')


# To do list
# Standardize time periods across versus and indiv classes
# Allow for time period parameters in indiv
# Make min and max time into a standard function
# Complete the cache
