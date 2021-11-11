import discord
from jstrisuser import UserAllStats
import jstrisfunctions
from discord.ext import commands
from jstrisfunctions import Parameter_Init

intents = discord.Intents.default()
intents.members = True
description = 'Third Party bot to quickly gather Jstris stats on individual players'

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def least(ctx, my_parameter, username: str, period: str, gamemode: str):
    my_ps = Parameter_Init(my_parameter, period, gamemode)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    await ctx.send("Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.least_(searched_games.all_stats, my_parameter)
        await ctx.send("Least for {} is: ".format(my_parameter) + str(a))


@bot.command()
async def most(ctx, my_parameter, username: str, period: str, gamemode: str):
    my_ps = Parameter_Init(my_parameter, period, gamemode)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    await ctx.send("Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.most_(searched_games.all_stats, my_parameter)
        await ctx.send("Most for {} is: ".format(my_parameter) + str(a))


@bot.command()
async def average(ctx, my_parameter, username: str, period: str, gamemode: str):
    my_ps = Parameter_Init(my_parameter, period, gamemode)
    if not my_ps.valid_params:
        await ctx.send("Invalid parameter")
    await ctx.send("Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.average_(searched_games.all_stats, my_parameter)
        await ctx.send("Average for {} is: ".format(my_parameter) + str(a))

@bot.command()
async def numgames(ctx, username: str, period: str, gamemode: str):
    my_parameter = None
    my_ps = Parameter_Init(my_parameter, period, gamemode)
    await ctx.send("Searching {}'s games now".format(username))
    searched_games = UserAllStats(username, my_ps.game, my_ps.mode, my_ps.period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = len(searched_games.all_stats)
        await ctx.send("{} games".format(str(a)))

if __name__ == "__main__":

    bot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')
