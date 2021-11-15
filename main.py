import discord
from discord.ext import commands
import jstrisfunctions
from jstrisfunctions import ParameterInit
from jstrisuser import UserIndivGames
from jstrisuser import UserLiveGames
import asyncio
from concurrent.futures import ThreadPoolExecutor

intents = discord.Intents.default()
intents.members = True
description = 'Third party bot to quickly gather Jstris stats on individual players'

bot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)
loop = asyncio.get_event_loop()
num_processes = 0


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def help(ctx):
    await ctx.send("https://docs.google.com/document/d/1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")


@bot.command()
async def least(ctx, username, *args):
    if not await num_processes_init(ctx):
        return None

    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send(ctx.author.mention)
        await ctx.send("Invalid parameter")

    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserIndivGames,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await num_processes_finish()

    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.least_(searched_games.all_stats, my_ps.param)
        await replay_send(ctx, a)


@bot.command()
async def most(ctx, username: str, *args):
    if not await num_processes_init(ctx):
        return None

    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send(ctx.author.mention)
        await ctx.send("Invalid parameter")

    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserIndivGames,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await num_processes_finish()

    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.most_(searched_games.all_stats, my_ps.param)
        await replay_send(ctx, a)


@bot.command()
async def average(ctx, username: str, *args):
    if not await num_processes_init(ctx):
        return None

    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send(ctx.author.mention)
        await ctx.send("Invalid parameter")

    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserIndivGames,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await num_processes_finish()
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.average_(searched_games.all_stats, my_ps.param)
        await ctx.send(ctx.author.mention)
        await ctx.send("Average {} for {} is: {}".format(my_ps.param, username, a))


@bot.command()
async def numgames(ctx, username: str, *args):
    # my_ps = ParameterInit(my_parameter, period, gamemode)
    if not await num_processes_init(ctx):
        return None

    my_ps = ParameterInit(args)
    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserIndivGames,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await num_processes_finish()

    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = len(searched_games.all_stats)
        await ctx.send(ctx.author.mention)
        await ctx.send("{} games".format(str(a)))


@bot.command()
async def sub300(ctx, username, period="alltime"):
    if not await num_processes_init(ctx):
        return None

    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))

    args = (period, '')
    my_ps = ParameterInit(args)
    period = my_ps.period
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserIndivGames,
                                                username, "3", "3", period)
    await num_processes_finish()
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        await ctx.send(searched_games.error_message)
    else:
        await ctx.send(ctx.author.mention)
        await ctx.send("{} has {} sub 300s".format(username, jstrisfunctions.sub300(searched_games.all_stats)))


@bot.command()
async def vs(ctx, username, offset=10):
    if not await num_processes_init(ctx):
        return None

    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await num_processes_finish()
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        # await ctx.send("Invalid username: {}".format(username))
        await ctx.send(searched_games.error_message)
        return None

    # Calculates averages
    apm_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'apm')
    spm_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'spm')
    pps_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'pps')
    time_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'gametime')
    players_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'players')
    pos_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'pos')
    won_games = jstrisfunctions.games_won(searched_games.all_stats, offset)

    # Discord formatting
    embed = await embed_init(username)
    embed.add_field(name="**apm:**", value=apm_avg, inline=True)
    embed.add_field(name="**spm:**", value=spm_avg, inline=True)
    embed.add_field(name="**pps:**", value=pps_avg, inline=True)
    embed.add_field(name="**time (seconds):**", value=time_avg, inline=True)
    embed.add_field(name="**final position:**", value=pos_avg, inline=True)
    embed.add_field(name="**players:**", value=players_avg, inline=True)
    embed.add_field(name="**games won:**", value=str(won_games), inline=False)
    embed.add_field(name="**number of games:**", value=str(offset), inline=False)
    embed.set_footer(text='All of these values are averages.')
    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command()
async def allmatchups(ctx, username):
    if not await num_processes_init(ctx):
        return None

    offset = 10000000000
    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await num_processes_finish()
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        # await ctx.send("Invalid username: {}".format(username))
        await ctx.send(searched_games.error_message)
        return None
    list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_stats)

    # Discord formatting stuff
    # Get top 10 opponents

    embed = await embed_init(username)

    c = 0
    for key in list_of_opponents:
        if key is None:
            continue
        embed.add_field(name='**opponent:**', value="{}. {}".format(c + 1, key), inline=True)
        embed.add_field(name='**games won (by user):**', value=list_of_opponents[key]["won"], inline=True)
        embed.add_field(name='**total games:**', value=list_of_opponents[key]["games"], inline=True)
        c += 1
        if c >= 8:
            break
    embed.set_footer(text='Only the top 8 players with most played games are shown here for technical reasons. '
                          'For individual match ups, try using ?indivmatchup instead. Also, Jstris will delete replays'
                          'over time, and they will not be counted here.')

    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command()
async def vsmatchup(ctx, username, opponent):
    if not await num_processes_init(ctx):
        return None
    offset = 10000000000
    init_message = await ctx.send("Searching {}'s games now. This can take a while.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await num_processes_finish()
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(ctx.author.mention)
        # await ctx.send("Invalid username: {}".format(username))
        await ctx.send(searched_games.error_message)
        return None
    list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_stats)
    embed = await embed_init(username)

    has_opponent = False
    for key in list_of_opponents:
        if key is None:
            continue
        if key.lower() == opponent.lower():
            has_opponent = True
            embed.add_field(name='**opponent:**', value=key, inline=True)
            embed.add_field(name='**games won:**', value=list_of_opponents[key]["won"], inline=True)
            embed.add_field(name='**total games:**', value=list_of_opponents[key]["games"], inline=True)
            embed.add_field(name='**apm:**', value=list_of_opponents[key]["apm"], inline=True)
            embed.add_field(name='**spm:**', value=list_of_opponents[key]["spm"], inline=True)
            embed.add_field(name='**pps:**', value=list_of_opponents[key]["pps"], inline=True)

    embed.set_footer(text='All stats here are for the player, not the opponent. To find the opponents stats, simply '
                          'call this command again in reverse. Also, Jstris will delete replays over time, and they '
                          'will not be counted here')

    if not has_opponent:
        await ctx.send(ctx.author.mention)
        await ctx.send("No found games of {} vs {}.".format(username, opponent))
        return None
    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)


async def replay_send(ctx, my_ps):
    embed = await embed_init(my_ps['username'])

    for i in my_ps:
        if i not in ("username", 'replay'):
            embed.add_field(name="**{}:**".format(i), value=my_ps[i], inline=False)
    if my_ps["replay"] != "- ":
        embed.add_field(name="**replay:**", value=my_ps['replay'], inline=False)
    else:
        embed.add_field(name="**replay:**", value="replay not available", inline=False)
    embed.set_footer(text='Have any suggestions? Please message Truebulge#0358 on Discord!')
    await ctx.send(ctx.author.mention)
    await ctx.send(embed=embed)


async def embed_init(username):
    embed = discord.Embed(
        title=username,
        url="https://jstris.jezevec10.com/u/{}".format(username),
        color=discord.Colour.red())
    embed.set_author(name="BadgerBot")
    embed.set_thumbnail(url="https://i.imgur.com/WDUv9f0.png")
    return embed


async def num_processes_init(ctx):
    global num_processes
    num_processes += 1
    if num_processes > 5:
        num_processes -= 1
        await ctx.send(ctx.author.mention)
        await ctx.send("Sorry, currently busy handling other requests. Please try again in a few minutes.")
        return False
    return True


async def num_processes_finish():
    global num_processes
    num_processes -= 1

if __name__ == "__main__":

    bot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')
