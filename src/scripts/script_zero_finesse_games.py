import pandas as pd
from lib.jstrisuser import UserIndivGames

def main():
    game = '3'
    mode = '3'

    usernames = [
        "VinceHD",
        "Whitestrake",
        "Opium",
        "toj_double",
        "hachicat",
        "Session",
        "z2sam",
        "Trampoline",
        "Hsterts",
        "youarefat",
        "mystery",
        "TangerineV2",
        "Feels",
        "albatross",
        "Googol",
        "TFW",
        "Reseffe",
        "Wenxiu",
        "Kirby703",
        "mars",
        "caffeine",
        "JohnSmithNumberSix",
        "kzl",
        "Skyfire",
        "kimwoon_",
        "Hericendre",
        "asdfg",
        "Hepta",
        "heri_no_ghost",
        "torchlight",
        "ybk1011",
    ]

    print(f"Searching {len(usernames)} players..")

    replays = []
    for i, username in enumerate(usernames):
        print(i + 1, username)
        user = UserIndivGames(username, game, mode)
        if user.has_error:
            raise Exception(user.has_error)
        replays.extend(user.all_replays)

    df = pd.DataFrame(replays)
    df.to_csv(f"raw_{game}_{mode}_replays.csv", index=False)

    # filter by 0 finesse
    df = df[df["finesse"] == 0]

    # get replay with least blocks for each username
    df = df.sort_values("blocks")
    df = df.groupby("username").head(1)

    df.to_csv(f"{game}_{mode}_replays.csv", index=False)

if __name__ == "__main__":
    main()