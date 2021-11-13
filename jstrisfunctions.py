import jstrisuser
import datetime


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

    stat_average = 0
    for i in list_of_runs:
        stat_average += i[my_param]
    return round(stat_average/len(list_of_runs), 3)


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


def period_str_to_int(my_str):
    if my_str in ('day', 'Day', 'today', 'Today'):
        return '1'
    elif my_str in ("week", 'Week'):
        return '2'
    elif my_str in ("month", "Month"):
        return "3"
    elif my_str in ("year", "Year"):
        return '4'
    if my_str in ('alltime', "Alltime"):
        return '0'
    return False


def is_valid_param(my_param, game):
    if game in ('ultra', 'Ultra') and my_param in ("ppb", 'PPB', 'Ppb'):
        return 'ppb'
    if game in ('ultra', 'Ultra') and my_param in ("score", 'Score'):
        return 'score'
    if game in ("pcmode", "PCmode") and my_param in ('pcs', 'PCS', 'PC', 'Pc', 'Pcs', 'pc'):
        return 'pcs'
    if game in ("20tsd", "20TSD") and my_param in ('tsds', 'TSDS', 'Tsds'):
        return 'tsds'
    if my_param in ('pps', 'PPS', 'Pps'):
        return 'pps'
    if my_param in ('blocks', 'Blocks'):
        return 'blocks'
    if my_param in ('finesse', 'Finesse'):
        return 'finesse'
    if my_param in ('time', 'Time'):
        return 'time'
    return False


def gamemode_init(my_str):
    if my_str == "sprint":
        return {"game": '1', "mode": "1"}
    elif my_str == "sprint20":
        return {"game": '1', "mode": "2"}
    elif my_str == "sprint40":
        return {"game": '1', "mode": "1"}
    elif my_str == "sprint100":
        return {"game": '1', "mode": "3"}
    elif my_str == "sprint1000":
        return {"game": '1', "mode": "1"}
    elif my_str == "cheese":
        return {"game": '3', "mode": "3"}
    elif my_str == "cheese10":
        return {"game": '3', "mode": "1"}
    elif my_str == "cheese18":
        return {"game": '3', "mode": "2"}
    elif my_str == "cheese100":
        return {"game": '3', "mode": "3"}
    elif my_str == "survival":
        return {"game": '4', "mode": "1"}
    elif my_str == "ultra":
        return {"game": '5', "mode": "1"}
    elif my_str == '20tsd':
        return {"game": '7', "mode": "1"}
    elif my_str == "pcmode":
        return {"game": '8', "mode": "1"}
    else:
        return False


class ParameterInit:
    valid_params = True
    game = ""
    period = ""
    mode = ""
    param = ""

    def __init__(self, my_parameter, period: str, gamemode: str):
        a = gamemode_init(gamemode)
        self.game = a["game"]
        self.mode = a["mode"]
        if not is_valid_param(my_parameter, gamemode):
            self.valid_params = False
        self.param = is_valid_param(my_parameter, self.game)
        self.period = period_str_to_int(period)


def parameter_init(my_tuple):
    gamemode = False
    period = False
    my_parameter = False

    for i in my_tuple:
        if gamemode_init(i):
            gamemode = i
        if period_str_to_int(i):
            period = i

    for i in my_tuple:
        if is_valid_param(i, gamemode):
            my_parameter = i

    if not gamemode:
        gamemode = "sprint"

    if not period:
        period = "alltime"

    if not my_parameter:
        if gamemode in ('ultra', 'Ultra'):
            my_parameter = "score"
        elif gamemode in ("20tsd", "20TSD"):
            my_parameter = "tsds"
        elif gamemode in ('pcs', 'PCS', 'PC', 'Pc', 'Pcs', 'pc'):
            my_parameter = "pcs"
        else:
            my_parameter = "time"

    return ParameterInit(my_parameter, period, gamemode)
