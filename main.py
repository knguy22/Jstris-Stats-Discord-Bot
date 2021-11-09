import discord
from jstrisuser import UserAllStats
import jstrisfunctions
from discord.ext import commands


# client = commands.Bot( command_prefix=" / " )

# @client.event
# async def on_ready( ):
#            print("Bot is ready")
#
#
# @client.event
# async def on_message(message):
#           if message.content == 'h':
#               await message.channel.send('bruh')

# Handles discord UI




# class MyClient(discord.Client):
#     async def on_connect(self):
#         print("Connected to Discord!")
#
#     async def on_disconnect(self):
#         print("Disconnected from Discord.")
#
#     async def on_ready(self):
#         print('Logged on as {0}!'.format(self.user))
#
#     async def on_message(self, message):
#         print('Message from {0.author}: {0.content}'.format(message))
#         if not message.author.bot and message.content[0] == '!':
#             message_list = message.content
#             message_list = message_list[1:]
#             message_list = message_list.split(" ")
#             username = message_list[0]
#             game = message_list[1]
#             mode = message_list[2]
#             period = message_list[3]
#             player_stats = UserAllStats(username=username,game=game,mode=mode,period=period)
#             a = player_stats.all_stats
#             if player_stats.has_error == True:
#                 await message.channel.send(player_stats.error_message)
#             # a = jstrisfunctions.recency_filter(list_of_runs=player_stats.all_stats, period=period)
#             a = jstrisfunctions.least_blocks(a)
#             await message.channel.send(a)

intents = discord.Intents.default()
intents.members = True
description = 'Third Party bot to quickly gather Jstris stats on individual players'

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def least(ctx, my_parameter, username: str, period: str, game: str, mode='0'):
    if not jstrisfunctions.least_most_param_init(my_parameter):
        await ctx.send("Invalid parameter")
    used_game = jstrisfunctions.game_str_to_int(game)
    used_period = jstrisfunctions.period_str_to_int(period)
    used_mode = jstrisfunctions.mode_str_to_int(mode, game)
    searched_games = UserAllStats(username, used_game, used_mode, used_period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.least_(searched_games.all_stats, my_parameter)
        await ctx.send("Least for {} is: ".format(my_parameter) + str(a))


@bot.command()
async def most(ctx, my_parameter, username: str, period: str, game: str, mode='0'):
    if not jstrisfunctions.least_most_param_init(my_parameter):
        await ctx.send("Invalid parameter")
    used_game = jstrisfunctions.game_str_to_int(game)
    used_period = jstrisfunctions.period_str_to_int(period)
    used_mode = jstrisfunctions.mode_str_to_int(mode, game)
    searched_games = UserAllStats(username, used_game, used_mode, used_period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.most_(searched_games.all_stats, my_parameter)
        await ctx.send("Most for {} is: ".format(my_parameter) + str(a))


@bot.command()
async def average(ctx, my_parameter, username: str, period: str, game: str, mode='0'):
    if not jstrisfunctions.least_most_param_init(my_parameter):
        await ctx.send("Invalid parameter")
    used_game = jstrisfunctions.game_str_to_int(game)
    used_period = jstrisfunctions.period_str_to_int(period)
    used_mode = jstrisfunctions.mode_str_to_int(mode, game)
    searched_games = UserAllStats(username, used_game, used_mode, used_period)
    if searched_games.has_error is True:
        await ctx.send(searched_games.error_message)
    else:
        a = jstrisfunctions.average_(searched_games.all_stats, my_parameter)
        await ctx.send("Average for {} is: ".format(my_parameter) + str(a))



if __name__ == "__main__":


    bot.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')


    # print(UserAllStats("Truebulge",'3','3','4').all_stats)
    # s = MyClient()
    # s.run("OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ")

    # game = '3'
    # mode = '3'
    # username = "orz"
    # player_stats = UserAllStats(username=username,game=game,mode=mode)
    # # a = jstrisstats.pc_finish_sprint(list_of_runs=player_stats.all_stats,mode=mode)
    # # a = jstrisstats.average_criteria(list_of_runs=player_stats.all_stats, criteria='blocks')
    # a = jstrisfunctions.recency_filter(list_of_runs=player_stats.all_stats, period='week')
    # a = jstrisfunctions.least_blocks(a)
    #
    # print(a)
    # print(len(a))