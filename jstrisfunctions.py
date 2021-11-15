import jstrisuser
import datetime


# Returns self.game, self.mode, self.period, self.param
# self.game, self.mode, and self.period are all strings of integers
# self.param is preserved as a string
# Ex: self.game = 1, self.mode = 2, self.period = 3
# self.param = finesse
class ParameterInit:
    valid_params = True
    gamemode = ""
    game = ""
    period = ""
    mode = ""
    param = ""

    def __init__(self, my_tuple):
        self.valid_params = True
        self.gamemode = ""
        self.game = ""
        self.period = ""
        self.mode = ""
        self.param = ""

        # NOTE: MY TUPLE MUST CONTAIN MORE THAN ONE INDEX FOR THIS TO WORK; ADD AN EXTRA EMPTY STRING IN THE
        # TUPLE IF NEEDED
        # checking for all settings in my_tuple

        for i in my_tuple:
            self.gamemode_init(i)
            self.period_str_to_int(i)

        for i in my_tuple:
            self.param_init(i, self.gamemode)

        # sets defaults for unspecified settings in my_tuple

        self.default_settings()
        print(self.game, self.mode, self.param, self.period, self.gamemode)

    def period_str_to_int(self, my_str):
        if my_str in ('day', 'Day', 'today', 'Today'):
            self.period = '1'
        elif my_str in ("week", 'Week'):
            self.period = '2'
        elif my_str in ("month", "Month"):
            self.period = "3"
        elif my_str in ("year", "Year"):
            self.period = '4'
        elif my_str in ('alltime', "Alltime"):
            self.period = '0'

    def param_init(self, my_param, game):
        if game in ('ultra', 'Ultra') and my_param in ("ppb", 'PPB', 'Ppb'):
            self.param = 'ppb'
        if game in ('ultra', 'Ultra') and my_param in ("score", 'Score'):
            self.param = 'score'
        if game in ("pcmode", "PCmode") and my_param in ('pcs', 'PCS', 'PC', 'Pc', 'Pcs', 'pc'):
            self.param = 'pcs'
        if game in ("20tsd", "20TSD") and my_param in ('tsds', 'TSDS', 'Tsds'):
            self.param = 'tsds'
        if my_param in ('pps', 'PPS', 'Pps'):
            self.param = 'pps'
        if my_param in ('blocks', 'Blocks'):
            self.param = 'blocks'
        if my_param in ('finesse', 'Finesse'):
            self.param = 'finesse'
        if my_param in ('time', 'Time'):
            self.param = 'time'

    def gamemode_init(self, my_str):
        a = False
        if my_str == "sprint":
            a = {"game": '1', "mode": "1", "gamemode": 'sprint'}
        elif my_str == "sprint20":
            a = {"game": '1', "mode": "2", "gamemode": 'sprint'}
        elif my_str == "sprint40":
            a = {"game": '1', "mode": "1", "gamemode": 'sprint'}
        elif my_str == "sprint100":
            a = {"game": '1', "mode": "3", "gamemode": 'sprint'}
        elif my_str == "sprint1000":
            a = {"game": '1', "mode": "1", "gamemode": 'sprint'}
        elif my_str == "cheese":
            a = {"game": '3', "mode": "3", "gamemode": 'cheese'}
        elif my_str == "cheese10":
            a = {"game": '3', "mode": "1", "gamemode": 'cheese'}
        elif my_str == "cheese18":
            a = {"game": '3', "mode": "2", "gamemode": 'cheese'}
        elif my_str == "cheese100":
            a = {"game": '3', "mode": "3", "gamemode": 'cheese'}
        elif my_str == "survival":
            a = {"game": '4', "mode": "1", "gamemode": 'survival'}
        elif my_str == "ultra":
            a = {"game": '5', "mode": "1", "gamemode": 'ultra'}
        elif my_str == '20tsd':
            a = {"game": '7', "mode": "1", "gamemode": '20tsd'}
        elif my_str == "pcmode":
            a = {"game": '8', "mode": "1", "gamemode": 'pcmode'}
        if a:
            self.game = a["game"]
            self.mode = a["mode"]
            self.gamemode = a["gamemode"]

    def default_settings(self):
        if self.gamemode == "":
            self.game = '1'
            self.mode = '1'

        if self.period == "":
            self.period = "alltime"
            self.period = 0

        if self.param == "":
            if self.gamemode in 'ultra':
                self.param = "score"
            elif self.gamemode in "20tsd":
                self.param = "tsds"
            elif self.gamemode in 'pc':
                self.param = "pcs"
            else:
                self.param = "time"


def sub300(listofruns):
    c = 0
    for i in listofruns:
        if i["blocks"] < 300:
            c += 1
    return c


def best_run(list_of_runs):
    return list_of_runs[0]


def least_(list_of_runs, my_param):
    if len(list_of_runs) == 0:
        return None

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrisuser.clock_to_seconds(x['time']), list_of_runs))
        c = 0
        for my_second in list_of_seconds:
            list_of_runs[c]['seconds'] = my_second
            c += 1

    final_run = sorted(list_of_runs, key=lambda x: x[my_param])[0]

    if my_param == "time":
        del final_run["seconds"]

    return final_run


def most_(list_of_runs, my_param):
    if len(list_of_runs) == 0:
        return None

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrisuser.clock_to_seconds(x['time']), list_of_runs))
        c = 0
        for my_second in list_of_seconds:
            list_of_runs[c]['seconds'] = my_second
            c += 1

    final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]

    if my_param == "time":
        del final_run["seconds"]

    return final_run


def average_(list_of_runs, my_param):

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrisuser.clock_to_seconds(x['time']), list_of_runs))
        c = 0
        for my_second in list_of_seconds:
            list_of_runs[c]['seconds'] = my_second
            c += 1

    stat_average = 0
    for i in list_of_runs:
        stat_average += i[my_param]

    if my_param == "seconds":
        return jstrisuser.seconds_to_clock(round(stat_average/len(list_of_runs), 2))
    return round(stat_average/len(list_of_runs), 2)


def pc_finish_sprint(list_of_runs, mode):
    lines = 0
    if mode == "2":
        lines = 20
    elif mode == "1":
        lines = 40
    elif mode == "3":
        lines = 100
    elif mode == "4":
        lines = 1000

    for i in list_of_runs:
        if i["blocks"] == lines*2.5:
            return i


def recency_filter(list_of_runs, period='alltime'):
    new_list_of_runs = []
    my_days = 0

    if period == 'day':
        my_days = 1
    elif period == 'week':
        my_days = 7
    elif period == 'month':
        my_days = 30
    elif period == 'year':
        my_days = 365
    elif period == 'alltime':
        return list_of_runs

    now = datetime.datetime.now()
    for i in list_of_runs:
        my_replay = datetime.datetime.strptime(i['date'], "%Y-%m-%d %H:%M:%S")
        if my_days > (now-my_replay).days:
            new_list_of_runs.append(i)

    return new_list_of_runs


def num_games(list_of_runs):
    return len(list_of_runs)


def livegames_avg(list_of_games, offset, param):
    c = 0
    summation = 0
    while c < offset:
        summation += list_of_games[c][param]
        c += 1
    return round(summation / offset, 2)


def livegames_weighted_avg(list_of_games, offset, param):
    c = 0
    summation = 0
    time_summation = 0
    while c < offset:
        summation += list_of_games[c][param]
        time_summation += list_of_games[c]["gametime"]
        c += 1
    return round(summation / time_summation, 2)


def games_won(list_of_games, offset):
    c = 0
    won_games = 0
    while c < offset:
        if list_of_games[c]["pos"] == 1:
            won_games += 1
        c += 1
    return won_games


def first_last_date(list_of_games):
    pass


def opponents_matchups(list_of_games):

    list_of_opponents = {}
    c = 0
    while c < len(list_of_games):
        if list_of_games[c]['players'] == 2:
            if list_of_games[c]['vs'] not in list_of_opponents:
                list_of_opponents[list_of_games[c]['vs']] = {"games": 1, "won": 0, "apm": 0, "spm": 0, "pps": 0,
                                                             'wapm': 0, 'wspm': 0, 'wpps': 0, 'time_sum': 0}
            else:
                list_of_opponents[list_of_games[c]['vs']]['games'] += 1

            if list_of_games[c]['pos'] == 1:
                list_of_opponents[list_of_games[c]['vs']]['won'] += 1
            list_of_opponents[list_of_games[c]['vs']]['apm'] += list_of_games[c]['apm']
            list_of_opponents[list_of_games[c]['vs']]['spm'] += list_of_games[c]['spm']
            list_of_opponents[list_of_games[c]['vs']]['pps'] += list_of_games[c]['pps']
            list_of_opponents[list_of_games[c]['vs']]['wapm'] += list_of_games[c]['attack']
            list_of_opponents[list_of_games[c]['vs']]['wspm'] += list_of_games[c]['sent']
            list_of_opponents[list_of_games[c]['vs']]['wpps'] += list_of_games[c]['pcs']
            list_of_opponents[list_of_games[c]['vs']]['time_sum'] += list_of_games[c]['gametime']

        c += 1

    for key in list_of_opponents:
        list_of_opponents[key]['apm'] = round(list_of_opponents[key]['apm'] / list_of_opponents[key]['games'], 2)
        list_of_opponents[key]['spm'] = round(list_of_opponents[key]['spm'] / list_of_opponents[key]['games'], 2)
        list_of_opponents[key]['pps'] = round(list_of_opponents[key]['pps'] / list_of_opponents[key]['games'], 2)
        list_of_opponents[key]['wapm'] = round(list_of_opponents[key]['wapm'] / list_of_opponents[key]['time_sum'] * 60, 2)
        list_of_opponents[key]['wspm'] = round(list_of_opponents[key]['wspm'] / list_of_opponents[key]['time_sum'] * 60, 2)
        list_of_opponents[key]['wpps'] = round(list_of_opponents[key]['wpps'] / list_of_opponents[key]['time_sum'], 2)

    # return list_of_opponents
    return dict(sorted(list_of_opponents.items(), key=lambda x: x[1]['games'], reverse=True))
