from typing import Union
import datetime
import pytz
import jstrishtml
import logging
import operator
import requests
import time

logger = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, filename="logjstris.log", datefmt='%m/%d/%Y %H:%M:%S',
                    format='%(levelname)s: %(module)s: %(message)s; %(asctime)s')


# Returns self.first and self.last as dates in the form of:
# 2021-10-29 09:25:55

class DateInit:

    def __init__(self, first: str, last: str) -> None:
        """

        :param first: str; first date;
        :param last: str; last date
        Date must be in calendar format or time ago format

        :return self.first: "%Y-%m-%d %H:%M:%S"
                self.last:"%Y-%m-%d %H:%M:%S"
        """

        self.first: str = first.lower()
        self.last: str = last.lower()
        self.has_error = False
        self.error_message = ""

        if self.if_datetime_format(self.first):
            pass
        elif self.check_if_calendar(self.first):
            self.first = self.calendar_to_date(self.first)
        else:
            self.first = self.is_time_ago_to_date(self.first)

        if self.if_datetime_format(self.last):
            pass
        elif self.check_if_calendar(self.last):
            self.last = self.calendar_to_date(self.last)
        else:
            self.last = self.is_time_ago_to_date(self.last)

        # Switches first and last if last is before first

        if not self.has_error:
            self.first_vs_last()
            logging.info(self)

        if self.has_error:
            logging.info(self.error_message)

    def if_datetime_format(self, string: str) -> bool:
        try:
            self.str_to_datetime(string)
            return True
        except ValueError:
            return False

    def calendar_to_date(self, string: str) -> Union[None, str]:

        num_year = datetime.datetime.now().year
        num_day = '01'

        months_dict = {'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
                       'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11',
                       'december': '12'}

        str_list = string.split(" ")
        str_list = [i.replace(',', '') for i in str_list]

        if str_list[0] in months_dict:
            num_month = months_dict[str_list[0]]
        else:
            self.has_error = True
            self.error_message = "Error: Not valid date formatting"
            return None

        if len(str_list) == 3:
            num_year = str_list[2]
            num_day = str_list[1]
        elif len(str_list) == 2:
            if int(str_list[1]) <= 31:
                num_day = str_list[1]
            else:
                num_year = str_list[1]
        elif len(num_day) == 1:
            num_day = "0" + num_day
        return f"{num_year}-{num_month}-{num_day} 00:00:00"

    def is_time_ago_to_date(self, string: str) -> Union[None, str]:
        now = datetime.datetime.now(tz=pytz.timezone('CET'))
        num_days = self.is_time_ago_to_days(string)
        if num_days is None:
            self.has_error = True
            self.error_message = f'Error: Not valid date formatting ("{string}")'
            return None
        my_date = now - datetime.timedelta(days=num_days)
        my_date = my_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]
        return my_date

    @staticmethod
    def is_time_ago_to_days(string: str) -> Union[None, int]:
        str_list = string.split(" ")
        num_days = 0
        num_months = 0
        days_list = ["days", 'Days', "day", "Day", "DAY", "DAYS"]
        months_list = ["months", 'Months', "month", "Month", "MONTH", "MONTHS"]

        if len(str_list) == 1:
            if str_list[0].lower() in ["day", 'today']:
                return 1
            if str_list[0].lower() == "week":
                return 7
            if str_list[0].lower() == 'month':
                return 30
            if str_list[0].lower() == 'year':
                return 365
            if str_list[0].lower() == 'alltime':
                return 10000000

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

    @staticmethod
    def str_to_datetime(string: str) -> datetime:

        if '+' in string:
            string = string[:-6]
        a = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        a = a.replace(tzinfo=pytz.timezone('CET'))
        return a

    @staticmethod
    def datetime_to_str_naive(s: datetime) -> str:
        s = str(s)
        if "+" in s:
            return s[:-6]
        return s

    @staticmethod
    def clock_to_seconds(s: str) -> float:
        """
        Input:
            string: {a}:{b}.{c} where a = minutes, b = seconds, c = milliseconds rounded to 3 digits
        Output:
            float: time in seconds
        """
        # format
        # 1:43.365
        minutes = 0
        milliseconds = 0
        colonindex = -1
        periodindex = len(s)
        if ':' in s:
            colonindex = s.index(":")
            minutes = int(s[: colonindex])
        if '.' in s:
            periodindex = s.index(".")
            milliseconds = float(s[periodindex + 1:]) / 1000
        seconds = int(s[colonindex + 1: periodindex])

        return round(60 * minutes + seconds + milliseconds, 3)
    
    
    @staticmethod
    def seconds_to_clock(s: float) -> str:
        if int(s) == s:
            return f"0:{s}"
        return str(datetime.timedelta(seconds=s))[2:-3]

    @staticmethod
    def seconds_to_timestr(s: float) -> str:
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        s = round(s, 3)
        m = int(m)
        h = int(h)

        s = str(s)
        if float(s) < 10:
            s = "0" + s
        # Adds 0 to end to add thousandth place (Ex: 0.22 -> 0.220)
        if len(s) == 5:
            s += '0'

        m = str(m)
        if int(m) < 10:
            m = "0" + m

        h = str(h)
        if int(h) < 10:
            h = "0" + h

        return f'{h} hours, {m} minutes, {s} seconds'

    def first_vs_last(self) -> None:
        try:
            first = self.str_to_datetime(self.first)
            last = self.str_to_datetime(self.last)
            if first > last:
                self.first, self.last = self.last, self.first
        except ValueError:
            self.has_error = True
            self.error_message = f'At least one date does not exist ({self.first}, {self.last})'

    def __repr__(self) -> str:
        if self.has_error:
            return f"DateInit({self.error_message})"
        return f"DateInit({self.first}, {self.last})"


# Returns self.game, self.mode, self.period, self.param
# Ex: self.game = 1, self.mode = 2, self.period = 3
# self.param = finesse

class IndivParameterInit:

    def __init__(self, my_tuple: tuple) -> None:
        self.gamemode = ""
        self.game = ""
        self.mode = ""
        self.param = ""
        self.first_date = ""
        self.last_date = ""
        self.comparisons = []
        self.has_error = False
        self.error_message = ""
        self.has_links = None

        logging.info(f"IndivParameterInit inputs: {my_tuple}")

        # NOTE: MY TUPLE MUST CONTAIN MORE THAN ONE INDEX FOR THIS TO WORK; ADD AN EXTRA EMPTY STRING IN THE
        # TUPLE IF NEEDED
        # checking for all settings in my_tuple

        for i in my_tuple:
            self.gamemode_init(i)

        for i in my_tuple:
            self.param_init(i, self.gamemode)

        # sets both self.first and self.last
        for i, j in enumerate(my_tuple):
            for k, l in enumerate(my_tuple):
                if i == k:
                    continue
                potential_dates = DateInit(first=j, last=l)
                if not potential_dates.has_error:
                    self.first_date = potential_dates.first
                    self.last_date = potential_dates.last
                    break
            else:
                continue
            break

        # sets only self.first
        if not self.first_date and not self.last_date:
            for i in my_tuple:
                potential_first_date = DateInit(first=i, last=i)
                if not potential_first_date.has_error:
                    self.first_date = potential_first_date.first
                    self.last_date = "9999-01-01 00:00:00"
                    break

        # sets defaults for unspecified settings in my_tuple

        self.default_settings()
        logging.info(self)

        # do comparisons; need to do comparisons after defaults are set
        for i in my_tuple:
            self.comparison_init(i)
            self.has_links_init(i)

    def param_init(self, my_param: str, game: str) -> None:
        my_param = my_param.lower()
        if game == 'ultra' and my_param == 'ppb':
            self.param = 'ppb'
        elif my_param == 'ppb' and game != 'ultra':
            self.has_error = True
            self.error_message = f'Error: parameter "{my_param}" not valid in gamemode "{game}"'

        if game == 'ultra' and my_param in ('score', 'point', 'points'):
            self.param = 'score'
        elif my_param == 'ppb' and game != 'ultra':
            self.has_error = True
            self.error_message = f'Error: parameter "{my_param}" not valid in gamemode "{game}"'

        if game == 'pcmode' and my_param in ('pcs', 'pc'):
            self.param = 'pcs'
        elif my_param in ('pcs', 'pc') and game != 'pcmode':
            self.has_error = True
            self.error_message = f'Error: parameter "{my_param}" not valid in gamemode "{game}"'

        if game == '20tsd' and my_param in ('tsds', 'tsd'):
            self.param = 'tsds'
        elif my_param == 'tsds' and game != '20tsd':
            self.has_error = True
            self.error_message = f'Error: parameter "{my_param}" not valid in gamemode "{game}"'

        if game == '20tsd' and my_param == '20tsd time':
            self.param = '20tsd time'
        elif my_param == 'tsds' and game != '20tsd':
            self.has_error = True
            self.error_message = f'Error: parameter "{my_param}" not valid in gamemode "{game}"'

        if my_param == 'pps':
            self.param = 'pps'
        if my_param in ('blocks', 'block'):
            self.param = 'blocks'
        if my_param == 'finesse':
            self.param = 'finesse'
        if my_param == 'time':
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
            a = {"game": '1', "mode": "4", "gamemode": 'sprint'}
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
            
    def comparison_init(self, my_comp: str):
        """
        Extracts necessary info for comparison; comparisons will be made in the following form:

        Parameter Operator Value (Exclude spaces)

        EX: finesse<5.4

        :param my_comp: str
        :return:
        """

        data_criteria = []
        if self.game in ('1', '3', '4'):
            data_criteria = ["time", "blocks", "pps", "finesse", "date"]
        elif self.game == '5':
            data_criteria = ["score", "blocks", "ppb", "pps", "finesse", "date"]
        elif self.game == '7':
            data_criteria = ["tsds", "time", "20tsd time", "blocks", "pps", "date"]
        elif self.game == '8':
            data_criteria = ["pcs", "time", "blocks", "pps", "finesse", "date"]

        comparison_operator = ""
        if ">=" in my_comp:
            comparison_operator = '>='
        elif "<=" in my_comp:
            comparison_operator = '<='
        elif "<" in my_comp:
            comparison_operator = '<'
        elif ">" in my_comp:
            comparison_operator = '>'
        elif "=" in my_comp:
            comparison_operator = '='

        # Param and value both avoid the operator
        comparison_param = my_comp[: my_comp.find(comparison_operator)]
        comparison_value = my_comp[my_comp.find(comparison_operator) + len(comparison_operator):]
        if comparison_operator == '=':
            comparison_operator = '=='

        if comparison_param in data_criteria:
            self.has_error = False
            self.error_message = ""
            if comparison_param == "date":
                a = DateInit(comparison_value, comparison_value)
                if not a.has_error:
                    self.comparisons.append({'param': 'date (CET)', 'value': DateInit.str_to_datetime(a.first),
                                             'operator': comparison_operator})
                else:
                    self.has_error = True
                    self.error_message = f'Error: comparison value is not in a valid date format: "{comparison_value}"'
            else:
                # Makes sure that comparison_value is a float
                try:
                    self.comparisons.append({'param': comparison_param, 'value': float(comparison_value),
                                             'operator': comparison_operator})
                except ValueError:
                    self.has_error = True
                    self.error_message = f'Error: comparison value is not numeric: "{comparison_value}"'
        elif comparison_param in ('link', 'links'):
            pass
        elif not self.comparisons and comparison_operator:
            self.has_error = True
            self.error_message = f'Error: comparison parameter "{comparison_param}" is not a valid parameter in your given gamemode: "{self.gamemode}"'

    def default_settings(self) -> None:
        if self.gamemode == "":
            self.game = '1'
            self.mode = '1'
            self.gamemode = "sprint"

        if self.param == "":
            if self.gamemode in 'ultra':
                self.param = "score"
            elif self.gamemode in "20tsd":
                self.param = "tsds"
            elif self.gamemode in 'pc':
                self.param = "pcs"
            else:
                self.param = "time"

        if not self.first_date and not self.last_date:
            self.first_date = "0001-01-01 00:00:00"
            self.last_date = "9999-01-01 00:00:00"
    
    def has_links_init(self, filter):
        filter = filter.lower()
        if filter in ("links=true", 'link=true'):
            self.has_links = True
        if filter in ("links=false", 'link=false'):
            self.has_links = False

    def __repr__(self) -> str:
        return f"IndivParameterInit({self.gamemode}, {self.game}, {self.mode}, {self.param}," \
               f" {self.first_date}, {self.last_date}, {self.comparisons}, {self.has_links}"


class VersusParameterInit:
    def __init__(self, my_tuple: tuple) -> None:
        self.first_date = ""
        self.last_date = ""
        self.offset = 1000000000
        self.comparisons = []
        self.has_error = False
        self.error_message = ""

        logging.info(f"VersusParameterInit inputs: {my_tuple}")

        # sets both self.first and self.last
        for i, j in enumerate(my_tuple):
            for k, l in enumerate(my_tuple):
                if i == k:
                    continue
                potential_dates = DateInit(first=j, last=l)
                if not potential_dates.has_error:
                    self.first_date = potential_dates.first
                    self.last_date = potential_dates.last
                    break
            else:
                continue
            break

        # sets only self.first
        if not self.first_date and not self.last_date:
            for i in my_tuple:
                potential_first_date = DateInit(first=i, last=i)
                if not potential_first_date.has_error:
                    self.first_date = potential_first_date.first
                    self.last_date = "9999-01-01 00:00:00"
                    break

        # sets defaults
        if not self.first_date and not self.last_date:
            self.first_date = "0001-01-01 00:00:00"
            self.last_date = "9999-01-01 00:00:00"

        # sets offset
        for i in my_tuple:
            if i.isdigit():
                self.offset = int(i)

        # sets comparisons if any
        for i in my_tuple:
            self.comparison_init(i)

    def comparison_init(self, my_comp: str):
        """
        Extracts necessary info for comparison; comparisons will be made in the following form:

        Parameter Operator Value (Exclude spaces)

        EX: finesse<5.4

        :param my_comp: str
        :return:
        """

        data_criteria = ['date', 'apm', 'spm', 'pps', 'wapm', 'wspm', "wpps", 'ren', 'time', 'pos', 'players']

        comparison_operator = ""
        if ">=" in my_comp:
            comparison_operator = '>='
        elif "<=" in my_comp:
            comparison_operator = '<='
        elif "<" in my_comp:
            comparison_operator = '<'
        elif ">" in my_comp:
            comparison_operator = '>'
        elif "=" in my_comp:
            comparison_operator = '='

        # Param and value both avoid the operator
        comparison_param = my_comp[: my_comp.find(comparison_operator)]
        comparison_value = my_comp[my_comp.find(comparison_operator) + len(comparison_operator):]
        if comparison_operator == '=':
            comparison_operator = '=='

        if comparison_param in data_criteria:
            self.has_error = False
            self.error_message = ""
            if comparison_param == "date":
                a = DateInit(comparison_value, comparison_value)
                if not a.has_error:
                    self.comparisons.append({'param': 'date (CET)', 'value': DateInit.str_to_datetime(a.first),
                                             'operator': comparison_operator})
                else:
                    self.has_error = True
                    self.error_message = f'Error: comparison value is not in a valid date format: "{comparison_value}"'
            else:
                # Makes sure that comparison_value is a float
                try:
                    self.comparisons.append({'value': float(comparison_value), 'param': comparison_param,
                                             'operator': comparison_operator})
                except ValueError:
                    self.has_error = True
                    self.error_message = f'Error: comparison value is not numeric: "{comparison_value}"'
        elif not self.comparisons and comparison_operator:
            self.has_error = True
            self.error_message = f'Error: comparison parameter "{comparison_param}" is not a valid parameter in your given gamemode: "vs"'

    def __repr__(self):
        return f"VersusParameterInit ({self.first_date}, {self.last_date}, {self.offset})"


def subblocks(listofruns: list, blocks: int) -> int:
    c = 0
    for i in listofruns:
        if i["blocks"] < blocks:
            c += 1
    return c


def best_run(list_of_runs: list) -> dict:
    return list_of_runs[0]


def least_(list_of_runs: list, my_param: str) -> dict:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: DateInit.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    if 'seconds' not in list_of_runs[0] and 'time' not in list_of_runs[0]:
        final_run = sorted(list_of_runs, key=lambda x: x[my_param])[0]
    else:
        final_run = sorted(list_of_runs, key=operator.itemgetter(my_param, 'time'))[0]

    if my_param == "seconds":
        del final_run["seconds"]

    return final_run


def most_(list_of_runs: list, my_param: str) -> dict:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: DateInit.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    # final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]
    if 'seconds' not in list_of_runs[0] and 'time' not in list_of_runs[0]:
        final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]
    else:
        final_run = sorted(list_of_runs, key=operator.itemgetter(my_param, 'time'))[-1]

    if my_param == "seconds":
        del final_run["seconds"]

    return final_run


def average_(list_of_runs: list, my_param: str) -> Union[float, str]:

    if my_param not in ("time", "20tsd time"):
        list_of_stats = [x[my_param] for x in list_of_runs]
        data_avg = round(sum(list_of_stats)/len(list_of_stats), 2)
    else:
        list_of_stats = [DateInit.clock_to_seconds(x[my_param]) for x in list_of_runs if x[my_param] != '-']
        data_avg = round(sum(list_of_stats)/len(list_of_stats), 2)
        data_avg = DateInit.seconds_to_clock(data_avg)

    return data_avg

def pc_finish_sprint(list_of_runs: list, mode: str) -> dict:
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
        time_summation += list_of_games[c]["time"]
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


def first_last_date(list_of_dates: list) -> tuple:

    num_check_dates = 5

    min_curr_date_and_prev_dates = list(range(num_check_dates + 1))
    for i, j in enumerate(min_curr_date_and_prev_dates):
        min_curr_date_and_prev_dates[i] = DateInit.str_to_datetime("9999-02-01 00:00:00") \
                                          + datetime.timedelta(days=i)

    max_curr_date_and_prev_dates = list(range(num_check_dates + 1))
    for i, j in enumerate(max_curr_date_and_prev_dates):
        max_curr_date_and_prev_dates[i] = DateInit.str_to_datetime("0001-02-01 00:00:00") \
                                          + datetime.timedelta(days=i)

    min_time = list_of_dates[-1]
    max_time = list_of_dates[0]

    if len(list_of_dates) > 6:

        # Min date

        list_of_dates.reverse()
        for m, n in enumerate(list_of_dates):

            min_curr_date_and_prev_dates.pop(-1)
            min_curr_date_and_prev_dates.insert(0, n)

            if sorted(min_curr_date_and_prev_dates, reverse=True) == min_curr_date_and_prev_dates:
                min_time = list_of_dates[m - num_check_dates]
                break

        # Max date

        list_of_dates.reverse()
        for m, n in enumerate(list_of_dates):

            max_curr_date_and_prev_dates.pop(-1)
            max_curr_date_and_prev_dates.insert(0, n)

            if sorted(max_curr_date_and_prev_dates) == max_curr_date_and_prev_dates:
                max_time = list_of_dates[m - num_check_dates]
                break

    return min_time, max_time


async def new_first_last_date(list_of_dates: list) -> Union[tuple, bool]:

    # Higher indices now mean ascending order
    # Skip pruning if there are only two replays
    still_pruning = False
    if len(list_of_dates) > 3:
        list_of_dates.reverse()
        still_pruning = True

    while still_pruning:
        still_pruning = False
        new_list_of_dates = []

        for j, k in enumerate(list_of_dates):

            if len(list_of_dates) == 0 or len(list_of_dates) == 1:
                return False

            # Checks last index of the list; ie the greatest date
            if j + 1 == len(list_of_dates):
                if k > new_list_of_dates[-1]:
                    new_list_of_dates.append(k)
                break

            # Keeps the first index because we can't compare it in between two numbers
            if j == 0:
                new_list_of_dates.append(k)
                continue

            # Sees if the date is in between its neighbors; keeps the index if it is
            if list_of_dates[j-1] < k < list_of_dates[j+1]:
                new_list_of_dates.append(k)
            else:
                still_pruning = True

        list_of_dates = new_list_of_dates

    # Checks first index to make sure a big first index didn't slip by
    if len(list_of_dates) >= 3:
        if list_of_dates[0] > list_of_dates[1] > list_of_dates[2]:
            list_of_dates.pop(0)
    elif len(list_of_dates) == 2:
        if list_of_dates[0] > list_of_dates[1]:
            list_of_dates.pop(0)

    # Edge cases where no pruning is needed

    if len(list_of_dates) == 1:
        min_time, max_time = list_of_dates[0], list_of_dates[0],
    elif len(list_of_dates) == 2:
        min_time, max_time = min(list_of_dates), max(list_of_dates)

    # Normal case; list now only has ordered dates
    else:
        min_time, max_time = list_of_dates[0], list_of_dates[-1]

    return DateInit.datetime_to_str_naive(min_time), DateInit.datetime_to_str_naive(max_time)


async def opponents_matchups(list_of_games: list, max_games: int) -> dict:

    all_opponents = {}

    # Summing stats for each replay for each opponent

    for game in list_of_games:
        # No FFA games
        if game['players'] == 2 and game['vs'] is not None:
            player_name = game['vs'].lower()

            # Initialize new opponent name
            if player_name not in all_opponents:
                all_opponents[player_name] = {"games": 1, "won": 0, "apm": 0, "spm": 0, "pps": 0,
                                              'wapm': 0, 'wspm': 0, 'wpps': 0, 'time_sum': 0, 'ren': 0,
                                              'min_time': "",
                                              'max_time': ""}
            elif all_opponents[player_name]['games'] == max_games:
                continue
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
            all_opponents[player_name]['time_sum'] += game['time']
            all_opponents[player_name]['ren'] += game['ren']

    # Finding min and max time for each opponent

    for opp in all_opponents:

        list_of_dates = []
        for game in list_of_games:
            if game['vs'] is None or game['players'] != 2:
                continue
            if game['vs'].lower() == opp:
                list_of_dates.append(DateInit.str_to_datetime(game['date (CET)']))

        # Finding min and max time for each opponent
        min_max_time = await new_first_last_date(list_of_dates)

        all_opponents[opp]['min_time'] = min_max_time[0]
        all_opponents[opp]['max_time'] = min_max_time[1]

    # Calculate averages for relevant stats

    for opp in all_opponents:
        all_opponents[opp]['apm'] = round(all_opponents[opp]['apm'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['spm'] = round(all_opponents[opp]['spm'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['pps'] = round(all_opponents[opp]['pps'] / all_opponents[opp]['games'], 2)
        all_opponents[opp]['wapm'] = round(all_opponents[opp]['wapm'] / all_opponents[opp]['time_sum'] * 60, 2)
        all_opponents[opp]['wspm'] = round(all_opponents[opp]['wspm'] / all_opponents[opp]['time_sum'] * 60, 2)
        all_opponents[opp]['wpps'] = round(all_opponents[opp]['wpps'] / all_opponents[opp]['time_sum'], 2)
        all_opponents[opp]['ren'] = round(all_opponents[opp]['ren'] / all_opponents[opp]['games'], 2)

    # return all_opponents
    return dict(sorted(all_opponents.items(), key=lambda x: x[1]['games'], reverse=True))


async def opponents_matchups_replays(list_of_games: list) -> dict:
    games_sorted_by_opponent = {}

    for game in list_of_games:
        if game['players'] != 2 or game['vs'] is None:
            continue
            
        player_name = game['vs'].lower()
        if player_name not in games_sorted_by_opponent:
            games_sorted_by_opponent[player_name] = [game]
        else:
            games_sorted_by_opponent[player_name].append(game)

    return games_sorted_by_opponent

async def check_user_exists(username:str) -> bool:
    my_url = f"https://jstris.jezevec10.com/api/u/{username}/live/games?offset=0"
    r = requests.get(my_url)
    page_request = r.json()
    if "error" in page_request:
        return False
    return True

if __name__ == "__main__":
    a = IndivParameterInit(("cheese","link=true",))
    print(a.has_links)
    print(a.has_error)
    pass
