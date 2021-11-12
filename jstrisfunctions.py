import jstrisuser
import datetime


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
    if my_str == 'day':
        return '1'
    elif my_str == "week":
        return '2'
    elif my_str == "month":
        return "3"
    elif my_str == "year":
        return '4'
    if my_str == 'alltime':
        return '0'
    return False


def least_most_param_init(my_param, game):
    if game == 'ultra' and my_param == "ppb":
        return True
    if game == "pcmode" and my_param == 'pcs':
        return True
    if game == "20tsd" and my_param == 'tsds':
        return True

    if my_param in ("blocks", 'pps', 'PPS', 'Pps', 'finesse', 'time'):
        return True
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
        if not least_most_param_init(my_parameter, gamemode):
            self.valid_params = False
        self.param = my_parameter
        self.period = period_str_to_int(period)
        a = gamemode_init(gamemode)
        self.game = a["game"]
        self.mode = a["mode"]


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
        if least_most_param_init(i, gamemode):
            my_parameter = i

    if not gamemode:
        gamemode = "sprint"

    if not period:
        period = "alltime"

    if not my_parameter:
        my_parameter = "time"

    return ParameterInit(my_parameter, period, gamemode)
