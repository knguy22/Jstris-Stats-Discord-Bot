import discord
from discord.ext import commands
import jstrisfunctions
from jstrisfunctions import ParameterInit
from jstrisuser import UserAllStats
from jstrisuser import UserLiveGames
import asyncio
from concurrent.futures import ThreadPoolExecutor

intents = discord.Intents.default()
intents.members = True
description = 'Third party bot to quickly gather Jstris stats on individual players'

bot = commands.Bot(command_prefix='?', description=description, intents=intents, help_command=None)
loop = asyncio.get_event_loop()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def help(ctx):
    await ctx.send("https://docs.google.com/document/d/1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing")


@bot.command()
async def least(ctx, username, *args):
    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserAllStats,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.least_(searched_games.all_stats, my_ps.param)
        await replay_send(ctx, a)


@bot.command()
async def most(ctx, username: str, *args):
    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserAllStats,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.most_(searched_games.all_stats, my_ps.param)
        await replay_send(ctx, a)


@bot.command()
async def average(ctx, username: str, *args):
    my_ps = ParameterInit(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserAllStats,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.average_(searched_games.all_stats, my_ps.param)
        await ctx.send("Average for {} is: ".format(my_ps.param) + str(a))


@bot.command()
async def numgames(ctx, username: str, *args):
    # my_ps = ParameterInit(my_parameter, period, gamemode)
    my_ps = ParameterInit(args)
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserAllStats,
                                                username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        a = len(searched_games.all_stats)
        await ctx.send("{} games".format(str(a)))


@bot.command()
async def sub300(ctx, username, period="alltime"):
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    args = (period, '')
    my_ps = ParameterInit(args)
    period = my_ps.period
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserAllStats,
                                                username, "3", "3", period)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send(searched_games.error_message)
    else:
        await ctx.send("{} has {} sub 300s".format(username, jstrisfunctions.sub300(searched_games.all_stats)))


@bot.command()
async def vs(ctx, username, offset=10):
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send("Invalid username: {}".format(username))
        return None

    # Calculates averages
    apm_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'apm')
    spm_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'spm')
    time_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'gametime')
    players_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'players')
    pos_avg = jstrisfunctions.livegames_avg(searched_games.all_stats, offset, 'pos')
    won_games = jstrisfunctions.games_won(searched_games.all_stats, offset)

    # Discord formatting
    embed = await embed_init(username)
    embed.add_field(name="apm: ", value=apm_avg, inline=True)
    embed.add_field(name="spm: ", value=spm_avg, inline=True)
    embed.add_field(name="time (seconds): ", value=time_avg, inline=True)
    embed.add_field(name="final position: ", value=pos_avg, inline=True)
    embed.add_field(name="players: ", value=players_avg, inline=True)
    embed.add_field(name="games won: ", value=str(won_games), inline=False)
    embed.add_field(name="number of games: ", value=str(offset), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def matchups(ctx, username):
    offset = 10000000000
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send("Invalid username: {}".format(username))
        return None
    list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_stats)

    # Discord formatting stuff
    # Get top 10 opponents

    embed = await embed_init(username)

    c = 0
    print(list_of_opponents)
    for key in list_of_opponents:
        embed.add_field(name='username:', value=key, inline=True)
        embed.add_field(name='games won (by user):', value=list_of_opponents[key]["won"], inline=True)
        embed.add_field(name='total games:', value=list_of_opponents[key]["games"], inline=True)
        c += 1
        if c >= 8:
            break
    embed.set_footer(text='Only the top 8 players with most played games are shown here for technical reasons. '
                          'For individual match ups, try using ?indivmatchup instead')

    # print(stuff)
    await ctx.send(embed=embed)


@bot.command()
async def indivmatchups(ctx, username):
    offset = 10000000000
    init_message = await ctx.send("Searching {}'s games now. Please wait.".format(username))
    searched_games = await loop.run_in_executor(ThreadPoolExecutor(),
                                                UserLiveGames,
                                                username, offset)
    await init_message.delete()
    if searched_games.has_error:
        await ctx.send("Invalid username: {}".format(username))
        return None
    list_of_opponents = jstrisfunctions.opponents_matchups(searched_games.all_stats)
    embed = await embed_init(username)

    for key in list_of_opponents:
        if key == username:
            embed.add_field(name='username:', value=key, inline=True)
            embed.add_field(name='games won (by user):', value=list_of_opponents[key]["won"], inline=True)
            embed.add_field(name='total games:', value=list_of_opponents[key]["games"], inline=True)


async def replay_send(ctx, my_ps):
    embed = await embed_init(my_ps['username'])

    for i in my_ps:
        if i not in ("username", 'replay'):
            embed.add_field(name=i+":", value=my_ps[i], inline=False)
    if my_ps["replay"] != "- ":
        embed.add_field(name="replay:", value=my_ps['replay'], inline=False)
    else:
        embed.add_field(name="replay:", value="replay not available", inline=False)
    embed.set_footer(text='Have any suggestions? Please message Truebulge#0358 on Discord!')
    await ctx.send(embed=embed)


async def embed_init(username):
    embed = discord.Embed(
        title=username,
        url="https://jstris.jezevec10.com/u/{}".format(username),
        color=discord.Colour.red())
    embed.set_author(name="BadgerBot")
    embed.set_thumbnail(url="https://i.imgur.com/WDUv9f0.png")
    return embed

if __name__ == "__main__":

    bot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')
