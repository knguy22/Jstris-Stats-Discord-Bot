import discord
from jstrisuser import user_all_stats
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

class MyClient(discord.Client):
    async def on_connect(self):
        print("Connected to Discord!")

    async def on_disconnect(self):
        print("Disconnected from Discord.")

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.author.bot is False:
            await message.channel.send(message.content)


if __name__ == "__main__":
    p = user_all_stats(username= "Riviclia", game= '3', mode= '3')
    print(p.all_stats)
    # client = MyClient()
    # client.run('OTA2NzEyOTE0Njc1Nzg5ODU1.YYcoNA.K2uerr4Q3kwY3Rj3RnLWTemZNbQ')