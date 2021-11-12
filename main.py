import discord
from jstrisuser import UserAllStats
import jstrisfunctions
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
description = 'Third Party bot to quickly gather Jstris stats on individual players'

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def least(ctx, username, *args):
    my_ps = jstrisfunctions.parameter_init(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Test: Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.least_(searched_games.all_stats, my_ps.param)
        await ctx.send("Least for {} is: ".format(my_ps.param) + str(a))


@bot.command()
async def most(ctx, username: str, *args):
    my_ps = jstrisfunctions.parameter_init(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Test: Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.most_(searched_games.all_stats, my_ps.param)
        await ctx.send("Most for {} is: ".format(my_ps.param) + str(a))


@bot.command()
async def average(ctx, username: str, *args):
    my_ps = jstrisfunctions.parameter_init(args)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    init_message = await ctx.send("Test: Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.average_(searched_games.all_stats, my_ps.param)
        await ctx.send("Average for {} is: ".format(my_ps.param) + str(a))


@bot.command()
async def numgames(ctx, username: str, *args):
    # my_ps = ParameterInit(my_parameter, period, gamemode)
    my_ps = jstrisfunctions.parameter_init(args)
    init_message = await ctx.send("Test: Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    await init_message.delete()
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = len(searched_games.all_stats)
        await ctx.send("{} games".format(str(a)))


if __name__ == "__main__":

    bot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')
