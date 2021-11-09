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


def game_str_to_int(my_str):
    if my_str == "sprint":
        return '1'
    elif my_str == "cheese":
        return '3'
    elif my_str == "survival":
        return "4"
    elif my_str == "ultra":
        return '5'
    elif my_str == '20tsd':
        return '7'
    elif my_str == "PCmode":
        return '8'
    else:
        return None


def period_str_to_int(my_str):
    if my_str == 'day':
        return '1'
    elif my_str == "week":
        return '2'
    elif my_str == "month":
        return "3"
    elif my_str == "year":
        return '4'
    return '0'


def mode_str_to_int(my_str, game):
    if my_str == '0':
        if game == "sprint":
            return "1"
        elif game == "cheese":
            return "3"
    elif game == "1":
        if my_str == "20":
            return "2"
        elif my_str == "40":
            return '1'
        elif my_str == "100":
            return '3'
        elif my_str == "1000":
            return '4'
    elif game == "3":
        if my_str == "10":
            return "1"
        elif my_str == "18":
            return "2"
        elif my_str == "100":
            return "3"
    return '-1'


def least_most_param_init(my_param):
    if my_param in ("blocks", 'pps', 'finesse', 'time'):
        return True
    return False
