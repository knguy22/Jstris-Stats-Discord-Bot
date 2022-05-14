# A file meant to show an application of the games fetching functions of this repo
# This file is not meant to be a part of the main badgerbot 

import os
import asyncio
import json
import requests
import cache
import jstrisfunctions

LOOP = asyncio.new_event_loop()
LOCK = asyncio.Lock()

def get_all_games(game_num: str, mode_num: str, gamemode_name:str, dirname:str):
    all_usernames = username_init(game_num, mode_num, filename="usernames")
    params = jstrisfunctions.IndivParameterInit((gamemode_name,))
    
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    for player in all_usernames:
        if os.path.exists(f"{dirname}/{player}.json"):
            continue
        
        curr = cache.CacheInit(player, params, LOCK)
        LOOP.run_until_complete(curr.fetch_all_games())
        with open(f"{dirname}/{player}.json", 'w', encoding="utf") as f:
            f.write(json.dumps(curr.returned_replays))

# Handles username file storage
def username_init(game: str, mode: str, filename: str) -> list:
    # Checking if the username file is empty

    request_usernames = False

    if not os.path.exists(filename):
        f = open(filename, 'x')
        f.close()

    with open(filename, "r", encoding='utf-8') as f:
        list_of_usernames = f.readlines()
        if len(list_of_usernames) < 1:
            request_usernames = True

    # gather usernames from jstris api if unorderedname.txt is empty
    # if already have usernames, gather usernames from unorderedname.txt
    if request_usernames:
        list_of_usernames = all_names_leaderboards(game=game, mode=mode)
        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(list_of_usernames)
    else:
        with open(filename, "r", encoding='utf-8') as f:
            list_of_usernames = f.readlines()
            list_of_usernames = map(lambda x: x.replace('\n', ''), list_of_usernames)

    return list_of_usernames


# Requests all pages
def all_names_leaderboards(game: str, mode: str) ->list:
    num_usernames = 500
    next_position = 0
    list_of_usernames = []

    while num_usernames == 500:
        curr_usernames = leaderboards_to_usernames(game=game, mode=mode, offset=str(next_position))
        num_usernames = len(curr_usernames)
        list_of_usernames.extend(curr_usernames)
        next_position += 500

    return list_of_usernames

# Requests one page
def leaderboards_to_usernames(game: str, mode: str, offset: str = '0') -> list:
    # game:
    # 1 = sprint, 3 = cheese, 4 = survival, 5 = ultra

    # mode: (for sprint/cheese)
    # 1 = 40L/10L, 2 = 20L/18L, 3 = 100L, 4 = 1000L
    # any other gamemode should be 1

    # offset:
    # offset of users

    if mode:
        url = f"https://jstris.jezevec10.com/api/leaderboard/{game}?mode={mode}&offset={offset}"
    else:
        url = f"https://jstris.jezevec10.com/api/leaderboard/{game}&offset={offset}"

    print(url)

    response = requests.get(url)
    data = response.json()
    names_list = []
    for i in data:
        names_list.append(i['name'].lower() + "\n")

    return names_list

            
if __name__ == "__main__":
    get_all_games(game_num='3', mode_num='3', gamemode_name='cheese100', dirname='cheesestats')