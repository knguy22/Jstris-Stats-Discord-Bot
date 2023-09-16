# Jstris Stats Discord Bot 

<a href="url"><img src="https://i.imgur.com/WDUv9f0.png" align="center" height="200" ></a>

## Overview

This is a Discord bot made to quickly gather player stats from [Jstris](https://jstris.jezevec10.com), a popular tetris client. If you want to get started querying your own Jstris playing statistics, you can join [this Discord server](https://discord.gg/vdYVCvvKT4).

## Commands

Each command is sent with a ```?``` prefix, followed by the command name. Then, other parameters are sent in succession, with each parameter separated by spaces. 

For example, if you want to get an average sprint game's statistics, run ```?avg [username] sprint```. After the bot finishes running, you'll be pinged alongside your results.
\
&nbsp;
\
&nbsp;
<br></br><img src="https://i.imgur.com/VHGwmQI.png" align="left" height="400" ><br></br>  
&nbsp;
\
&nbsp;
\
You can also add more paremeters limiting to certain dates or even certain block counts. In the following case below, I've added parameters to check average sub 300 cheese runs for a month, using this command:
```?avg [username] cheese blocks<300 "date>[min date]" "date<[max date]"```.  
&nbsp;
\
&nbsp;
<br></br><img src="https://i.imgur.com/ZXlTaWh.png" align="left" height="400" ><b></b>  
\
&nbsp;
\
&nbsp;
For comprehensive documentation about the commands, please refer to this [document](https://docs.google.com/document/d/1D54qjRTNmkOBXcvff1vpiph5E5txnd6J6R2oI9e6ZMM/edit?usp=sharing).

## Development

If you want to host your own Discord bot using this code base as a starter, there are some implemention details that you need to pay attention to. Every Discord Bot requires a token to be used, so you'd need to register one with Discord in order to start using its Api. That token then needs to be stored in a single line in ```token.txt```.

Similarly, this project has hashed out an agreement with Jstris to not block this bot. A header is used by this bot to identify itself, and it has not been published to this repository. When creating your own bot, make sure to add your own unique header in ```header.txt```