import datetime
import jstrishtml
import logging
logger = logging.getLogger(__name__)


# Returns self.first and self.last as dates in the form of:
# 2021-10-29 09:25:55

class LiveDateInit:

    def __init__(self, first: str, last: str) -> None:
        """

        :param first: str; first date;
        :param last: str; last date
        Date must be in calendar format or time ago format

        :return self.first: "%Y-%m-%d %H:%M:%S"
                self.last:"%Y-%m-%d %H:%M:%S"
        """

        logging.info(f"LiveDateInit inputs: {first} {last}")

        self.first: str = first.lower()
        self.last: str = last.lower()
        self.has_error = False
        self.error_message = ""

        if self.check_if_calendar(self.first):
            self.first = self.calendar_to_date(self.first)
        else:
            self.first = self.is_time_ago_to_date(self.first)

        if self.check_if_calendar(self.last):
            self.last = self.calendar_to_date(self.last)
        else:
            self.last = self.is_time_ago_to_date(self.last)

        # Switches first and last if last is before first

        if not self.has_error:
            self.first_vs_last()
            logging.info(self)

        if self.has_error:
            logging.info(self.error_message)

    def calendar_to_date(self, string: str) -> [None, str]:

        num_year = datetime.datetime.now().year
        num_day = '01'

        months_dict = {'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
                       'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11',
                       'december': '12'}

        str_list = string.split(" ")

        if str_list[0] in months_dict:
            num_month = months_dict[str_list[0]]
        else:
            self.has_error = True
            self.error_message = "Error: Not valid date formatting"
            return None

        if len(str_list) >= 2:
            num_day = str_list[1][0]
        if len(str_list) == 3:
            num_year = str_list[2]
        if len(num_day) == 1:
            num_day = "0" + num_day
        return f"{num_year}-{num_month}-{num_day} 00:00:00"

    def is_time_ago_to_date(self, string: str) -> [None, str]:
        now = datetime.datetime.now()
        num_days = self.is_time_ago_to_days(string)
        if num_days is None:
            self.has_error = True
            self.error_message = f'Error: Not valid date formatting ("{string}")'
            return None
        my_date = now - datetime.timedelta(days=num_days)
        my_date = my_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]
        return my_date

    @staticmethod
    def is_time_ago_to_days(string: str) -> [None, int]:
        str_list = string.split(" ")
        num_days = 0
        num_months = 0
        days_list = ["days", 'Days', "day", "Day", "DAY", "DAYS"]
        months_list = ["months", 'Months', "month", "Month", "MONTH", "MONTHS"]

        if not set(str_list) & set(days_list) and not set(str_list) & set(months_list):
            return None

        for days in days_list:
            if days in str_list:
                days_index = str_list.index(days)
                num_days += int(str_list[days_index - 1])

        for months in months_list:
            if months in str_list:
                months_index = str_list.index(months)
                num_months += int(str_list[months_index - 1]) * 30

        return num_months + num_days

    @staticmethod
    def check_if_calendar(string: str) -> bool:
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
                  'november', 'december']
        string_list = string.split(" ")
        is_time_ago = False
        for value in string_list:
            if value in months:
                is_time_ago = True
        return is_time_ago

    def first_vs_last(self) -> None:
        first = datetime.datetime.strptime(self.first, "%Y-%m-%d %H:%M:%S")
        last = datetime.datetime.strptime(self.last, "%Y-%m-%d %H:%M:%S")
        if first > last:
            self.first, self.last = self.last, self.first

    def __repr__(self) -> str:
        if self.has_error:
            return f"LiveDateInit({self.error_message})"
        return f"LiveDateInit(first: {self.first}, last: {self.last})"


# Returns self.game, self.mode, self.period, self.param
# Ex: self.game = 1, self.mode = 2, self.period = 3
# self.param = finesse

class IndivParameterInit:

    def __init__(self, my_tuple: tuple) -> None:
        self.gamemode = ""
        self.game = ""
        self.period = ""
        self.mode = ""
        self.param = ""

        logging.info(f"IndivParameterInit inputs: {my_tuple}")

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
        logging.info(self)

    def period_str_to_int(self, my_str: str) -> None:
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

    def param_init(self, my_param: str, game: str) -> None:
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

    def gamemode_init(self, my_str: str) -> None:
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

    def default_settings(self) -> None:
        if self.gamemode == "":
            self.game = '1'
            self.mode = '1'
            self.gamemode = "sprint"

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

    def __repr__(self) -> str:
        return f"IndivParameterInit(gamemode: {self.gamemode}, game: {self.game}, " \
               f"mode: {self.mode}, period: {self.period}, param: {self.param})"


def sub300(listofruns: list) -> int:
    c = 0
    for i in listofruns:
        if i["blocks"] < 300:
            c += 1
    return c


def best_run(list_of_runs: list) -> dict:
    return list_of_runs[0]


def least_(list_of_runs: list, my_param: str) -> dict:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrishtml.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    final_run = sorted(list_of_runs, key=lambda x: x[my_param])[0]

    if my_param == "time":
        del final_run["seconds"]

    return final_run


def most_(list_of_runs: list, my_param: str) -> dict:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrishtml.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]

    if my_param == "time":
        del final_run["seconds"]

    return final_run


def average_(list_of_runs: list, my_param: str) -> [float, str]:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrishtml.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    stat_average = 0
    for i in list_of_runs:
        stat_average += i[my_param]

    if my_param == "seconds":
        return jstrishtml.seconds_to_clock(round(stat_average/len(list_of_runs), 2))
    return round(stat_average/len(list_of_runs), 2)


def pc_finish_sprint(list_of_runs: list, mode: str) -> int:
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
        if i["blocks"] == lines * 2.5:
            return i


def live_games_avg(list_of_games: list, offset: int, param: str) -> float:
    c = 0
    summation = 0
    while c < offset:
        summation += list_of_games[c][param]
        c += 1
        if c == len(list_of_games):
            break
    return round(summation / len(list_of_games), 2)


def live_games_weighted_avg(list_of_games: list, offset: int, param: str) -> float:
    c = 0
    summation = 0
    time_summation = 0
    while c < offset:
        summation += list_of_games[c][param]
        time_summation += list_of_games[c]["gametime"]
        c += 1
        if c == len(list_of_games):
            break
    return round(summation / time_summation, 2)


def games_won(list_of_games: list, offset: int) -> int:
    c = 0
    won_games = 0
    while c < offset:
        if list_of_games[c]["pos"] == 1:
            won_games += 1
        c += 1
        if c == len(list_of_games):
            break
    return won_games


def first_last_date(list_of_games: list) -> dict:
    min_time = str(list_of_games[-1]["gtime"])
    max_time = str(list_of_games[1]["gtime"])

    return {"min_time": min_time, "max_time": max_time}


def opponents_matchups(list_of_games: list) -> dict:

    all_opponents = {}

    # Summing stats for each replay for each opponent

    for game in list_of_games:
        # No FFA games
        if game['players'] == 2 and game['vs'] is not None:
            player_name = game['vs'].lower()

            # Initialize new opponent name
            if player_name not in all_opponents:
                all_opponents[player_name] = {"games": 1, "won": 0, "apm": 0, "spm": 0, "pps": 0,
                                              'wapm': 0, 'wspm': 0, 'wpps': 0, 'time_sum': 0,
                                              'min_time': "",
                                              'max_time': ""}
            else:
                all_opponents[player_name]['games'] += 1

            if game['pos'] == 1:
                all_opponents[player_name]['won'] += 1

            all_opponents[player_name]['apm'] += game['apm']
            all_opponents[player_name]['spm'] += game['spm']
            all_opponents[player_name]['pps'] += game['pps']
            all_opponents[player_name]['wapm'] += game['attack']
            all_opponents[player_name]['wspm'] += game['sent']
            all_opponents[player_name]['wpps'] += game['pcs']
            all_opponents[player_name]['time_sum'] += game['gametime']

    # Finding min and max time for each opponent

    for opp in all_opponents:

        list_of_dates = []
        for game in list_of_games:
            if game['vs'] is None or game['players'] != 2:
                continue
            if game['vs'].lower() == opp:
                list_of_dates.append(datetime.datetime.strptime(game['gtime'], "%Y-%m-%d %H:%M:%S"))

        min_time = list_of_dates[-1]
        max_time = list_of_dates[0]

        if len(list_of_dates) > 3:
            for m, n in enumerate(list_of_dates):
                if list_of_dates[-m - 2] > list_of_dates[-m - 1] > min_time:
                    break
                min_time = list_of_dates[-m - 1]

            for m, n in enumerate(list_of_dates):
                if list_of_dates[m + 2] < list_of_dates[m + 1] < max_time:
                    break
                max_time = list_of_dates[m + 1]

        all_opponents[opp]['min_time'] = str(min_time)
        all_opponents[opp]['max_time'] = str(max_time)

    # Calculate averages for relevant stats

    for opp in all_opponents:
        all_opponents[opp]['apm'] = round(all_opponents[opp]['apm'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['spm'] = round(all_opponents[opp]['spm'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['pps'] = round(all_opponents[opp]['pps'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['wapm'] = round(all_opponents[opp]['wapm'] / all_opponents[opp]['time_sum'] * 60, 2)
        all_opponents[opp]['wspm'] = round(all_opponents[opp]['wspm'] / all_opponents[opp]['time_sum'] * 60, 2)
        all_opponents[opp]['wpps'] = round(all_opponents[opp]['wpps'] / all_opponents[opp]['time_sum'], 2)

    # return all_opponents
    return dict(sorted(all_opponents.items(), key=lambda x: x[1]['games'], reverse=True))


if __name__ == "__main__":
    first_date = 'asdfasgd'
    second_date = 'march 5, 2021'
    h = LiveDateInit(first_date, second_date)
    print(h)
    print(h.error_message)
    g = IndivParameterInit(("asdfasdgasdg", "laksjdflkajsf"))
    print(g)
