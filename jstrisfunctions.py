import datetime
import pytz
import jstrishtml
import logging
import operator

logger = logging.getLogger(__name__)


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

    def calendar_to_date(self, string: str) -> [None, str]:

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

    def is_time_ago_to_date(self, string: str) -> [None, str]:
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
    def is_time_ago_to_days(string: str) -> [None, int]:
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

    def param_init(self, my_param: str, game: str) -> None:
        my_param = my_param.lower()
        if game == 'ultra' and my_param == 'ppb':
            self.param = 'ppb'
        if game == 'ultra' and my_param == 'score':
            self.param = 'score'
        if game == 'pcmode' and my_param in ('pcs', 'pc'):
            self.param = 'pcs'
        if game == '20tsd' and my_param == 'tsds':
            self.param = 'tsds'
        if game == '20tsd' and my_param == '20tsd time':
            self.param = '20tsd time'
        if my_param == 'pps':
            self.param = 'pps'
        if my_param == 'blocks':
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

    def __repr__(self) -> str:
        return f"IndivParameterInit({self.gamemode}, {self.game}, {self.mode}, {self.param}," \
               f" {self.first_date}, {self.last_date})"


class VersusParameterInit:
    def __init__(self, my_tuple: tuple) -> None:
        self.first_date = ""
        self.last_date = ""
        self.offset = 1000000000

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
        list_of_seconds = list(map(lambda x: jstrishtml.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    if 'seconds' not in list_of_runs[0] or 'time' not in list_of_runs[0]:
        final_run = sorted(list_of_runs, key=lambda x: x[my_param])[0]
    else:
        final_run = sorted(list_of_runs, key=operator.itemgetter('blocks','time'))[0]

    if my_param == "seconds":
        del final_run["seconds"]

    return final_run


def most_(list_of_runs: list, my_param: str) -> dict:

    if my_param == "time":
        my_param = 'seconds'
        list_of_seconds = list(map(lambda x: jstrishtml.clock_to_seconds(x['time']), list_of_runs))
        for c, my_second in enumerate(list_of_seconds):
            list_of_runs[c]['seconds'] = my_second

    # final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]
    if 'seconds' not in list_of_runs[0] or 'time' not in list_of_runs[0]:
        final_run = sorted(list_of_runs, key=lambda x: x[my_param])[-1]
    else:
        final_run = sorted(list_of_runs, key=operator.itemgetter('blocks', 'time'))[-1]

    if my_param == "seconds":
        del final_run["seconds"]

    return final_run


def average_(list_of_runs: list, my_param: str) -> [float, str]:

    # Converts time to datetime to prepare everything
    if my_param == "time" or my_param == '20tsd time':
        new_list_of_runs = []
        for i in list_of_runs:
            # Sometimes time is not saved
            if i[my_param] != '-':
                new_list_of_runs.append({'seconds': jstrishtml.clock_to_seconds(i[my_param])})
        my_param = 'seconds'
        list_of_runs = new_list_of_runs

    stat_average = 0
    numgames = 0

    for i in list_of_runs:
        stat_average += i[my_param]
        numgames += 1
    if my_param == "seconds":
        return str(datetime.timedelta(seconds=round(stat_average / numgames, 2)))[:-3]
    return round(stat_average/len(list_of_runs), 2)


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


async def new_first_last_date(list_of_dates: list) -> (tuple, bool):

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
            all_opponents[player_name]['time_sum'] += game['gametime']
            all_opponents[player_name]['ren'] += game['ren']

    # Finding min and max time for each opponent

    for opp in all_opponents:

        list_of_dates = []
        for game in list_of_games:
            if game['vs'] is None or game['players'] != 2:
                continue
            if game['vs'].lower() == opp:
                list_of_dates.append(DateInit.str_to_datetime(game['gtime']))

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


if __name__ == "__main__":
    # first_date = 'august 2010'
    # second_date = 'september 2020'
    # h = DateInit(first_date, second_date)
    # print(h)
    g = IndivParameterInit(('december 8', 'november 1', ''))
    print(g)

    # first = 'today'
    # second = '2021-10-05 01:23:56'
    first = ''
    second = ''
    nums = ''
    # nums = '10'

    print(VersusParameterInit((first, second, nums)))
    # test_list_of_games = [{"id":115200078, "gid": "2LVYPT", "cid":51591546, "gametime":17.65, "sent":4, "attack":4, "pcs":27, "players":5, "r1v1":0, "pos":5, "vs": "luliz", "gtime": "2021-01-01 21:36:18"}, {"id":115200028, "gid": "1K4SHL", "cid":51591546, "gametime":83.79, "sent":54, "attack":68, "pcs":151, "players":5, "r1v1":0, "pos":1, "vs": "luliz", "gtime": "2021-01-01 21:35:17"}, {"id":115199760, "gid": "3P64B8", "cid":51591546, "gametime":73.11, "sent":67, "attack":71, "pcs":126, "players":5, "r1v1":0, "pos":1, "vs": "luliz", "gtime": "2021-01-01 21:33:47"}, {"id":115199566, "gid": "ISRNU8", "cid":51591546, "gametime":43.08, "sent":38, "attack":45, "pcs":73, "players":6, "r1v1":0, "pos":2, "vs": "luliz", "gtime": "2021-01-01 21:32:30"}, {"id":115199436, "gid": "8ZQKGM", "cid":51591546, "gametime":99.14, "sent":46, "attack":68, "pcs":124, "players":7, "r1v1":0, "pos":2, "vs": "luliz", "gtime": "2021-01-01 21:31:43"}, {"id":115199169, "gid": "SM8C3X", "cid":51591546, "gametime":56.92, "sent":51, "attack":60, "pcs":88, "players":6, "r1v1":0, "pos":2, "vs": "luliz", "gtime": "2021-01-01 21:30:01"}, {"id":115199008, "gid": "5YQFX9", "cid":51591546, "gametime":112.67, "sent":95, "attack":100, "pcs":180, "players":6, "r1v1":0, "pos":1, "vs": "luliz", "gtime": "2021-01-01 21:29:00"}, {"id":115198662, "gid": "XSK8D6", "cid":51591546, "gametime":137.79, "sent":77, "attack":96, "pcs":246, "players":6, "r1v1":0, "pos":2, "vs": "luliz", "gtime": "2021-01-01 21:27:02"}, {"id":115198216, "gid": "OMX074", "cid":51591546, "gametime":32.33, "sent":13, "attack":15, "pcs":40, "players":6, "r1v1":0, "pos":4, "vs": "luliz", "gtime": "2021-01-01 21:24:40"}, {"id":115180467, "gid": "HTR8QI", "cid":51583434, "gametime":54.3, "sent":37, "attack":51, "pcs":83, "players":3, "r1v1":0, "pos":2, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:37:28"}, {"id":115180306, "gid": "OURBDL", "cid":51583434, "gametime":71.78, "sent":45, "attack":62, "pcs":123, "players":3, "r1v1":0, "pos":1, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:36:29"}, {"id":115180130, "gid": "ANHS7R", "cid":51583434, "gametime":28.3, "sent":19, "attack":24, "pcs":55, "players":3, "r1v1":0, "pos":1, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:35:14"}, {"id":115180036, "gid": "ARY5B1", "cid":51583434, "gametime":49.13, "sent":31, "attack":37, "pcs":90, "players":3, "r1v1":0, "pos":3, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:34:42"}, {"id":115179874, "gid": "H9EOVT", "cid":51583434, "gametime":27.9, "sent":23, "attack":23, "pcs":49, "players":3, "r1v1":0, "pos":1, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:33:47"}, {"id":115179792, "gid": "EKUFS6", "cid":51583434, "gametime":76.01, "sent":69, "attack":88, "pcs":138, "players":2, "r1v1":0, "pos":1, "vs": "chickennuggetsz", "gtime": "2021-01-01 19:33:12"}, {"id":115179564, "gid": "CXLQAK", "cid":51583434, "gametime":27.29, "sent":0, "attack":30, "pcs":42, "players":1, "r1v1":0, "pos":1, "gtime": "2021-01-01 19:31:53"}, {"id":115179438, "gid": "2OVKMC", "cid":51583434, "gametime":85.72, "sent":73, "attack":98, "pcs":165, "players":3, "r1v1":0, "pos":1, "vs": "Exyph", "gtime": "2021-01-01 19:31:08"}, {"id":115179221, "gid": "9WMENH", "cid":51583434, "gametime":98.18, "sent":67, "attack":83, "pcs":169, "players":4, "r1v1":0, "pos":1, "vs": "Exyph", "gtime": "2021-01-01 19:29:37"}, {"id":115178905, "gid": "B3LL1D", "cid":51583434, "gametime":101.9, "sent":61, "attack":65, "pcs":155, "players":4, "r1v1":0, "pos":3, "vs": "Exyph", "gtime": "2021-01-01 19:27:54"}, {"id":115172057, "gid": "X4KIKH", "cid":51580399, "gametime":178.44, "sent":152, "attack":170, "pcs":285, "players":36, "r1v1":0, "pos":2, "vs": "Pentioom78", "gtime": "2021-01-01 18:46:09"}, {"id":115171531, "gid": "Q69IR7", "cid":51580399, "gametime":176.19, "sent":113, "attack":132, "pcs":299, "players":37, "r1v1":0, "pos":9, "vs": "goscinny", "gtime": "2021-01-01 18:43:05"}, {"id":115037378, "gid": "KY59H5", "cid":51533415, "gametime":95.77, "sent":65, "attack":85, "pcs":179, "players":3, "r1v1":0, "pos":2, "vs": "ApplePie60", "gtime": "2021-01-01 05:55:51"}, {"id":115036988, "gid": "LD754F", "cid":51533415, "gametime":72.8, "sent":47, "attack":57, "pcs":115, "players":3, "r1v1":0, "pos":2, "vs": "K_3_V_R_A_L", "gtime": "2021-01-01 05:54:10"}, {"id":115036616, "gid": "IMYOXR", "cid":51533415, "gametime":28.52, "sent":22, "attack":23, "pcs":36, "players":4, "r1v1":0, "pos":4, "vs": "ApplePie60", "gtime": "2021-01-01 05:52:53"}, {"id":115015764, "gid": "6DSGDC", "cid":51524543, "gametime":20.2, "sent":2, "attack":2, "pcs":30, "players":6, "r1v1":0, "pos":5, "vs": "lagne", "gtime": "2020-08-25 13:29:56"}, {"id":114972730, "gid": "GSA4TA", "cid":51503692, "gametime":41.99, "sent":22, "attack":31, "pcs":85, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:17:13"}, {"id":114972589, "gid": "MWVG4F", "cid":51503692, "gametime":113.18, "sent":93, "attack":122, "pcs":224, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:16:22"}, {"id":114972270, "gid": "NMN0UH", "cid":51503692, "gametime":109.13, "sent":82, "attack":105, "pcs":207, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:14:15"}, {"id":114971922, "gid": "K0ZKOA", "cid":51503692, "gametime":50.31, "sent":47, "attack":47, "pcs":85, "players":2, "r1v1":0, "pos":1, "vs": "akatsuki16", "gtime": "2021-01-01 00:12:17"}, {"id":114971765, "gid": "5T3WYD", "cid":51503692, "gametime":70.34, "sent":65, "attack":94, "pcs":132, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:11:18"}, {"id":114971527, "gid": "HGXS11", "cid":51503692, "gametime":39.51, "sent":23, "attack":29, "pcs":62, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:10:03"}, {"id":114971359, "gid": "HEV2Q2", "cid":51503692, "gametime":52.27, "sent":44, "attack":53, "pcs":97, "players":2, "r1v1":0, "pos":1, "vs": "akatsuki16", "gtime": "2021-01-01 00:08:58"}, {"id":114971197, "gid": "STT9TZ", "cid":51503692, "gametime":24.47, "sent":8, "attack":9, "pcs":50, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:08:01"}, {"id":114971096, "gid": "8IDINQ", "cid":51503692, "gametime":105.81, "sent":52, "attack":72, "pcs":191, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:07:29"}, {"id":114970797, "gid": "S1D36C", "cid":51503692, "gametime":27.08, "sent":34, "attack":36, "pcs":55, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-01-01 00:05:34"}, {"id":114970631, "gid": "RM8IGK", "cid":51503692, "gametime":39.67, "sent":24, "attack":25, "pcs":65, "players":2, "r1v1":0, "pos":1, "vs": "akatsuki16", "gtime": "2021-01-01 00:04:40"}, {"id":114970495, "gid": "SVVRGH", "cid":51503692, "gametime":122.77, "sent":69, "attack":110, "pcs":242, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2022-09-29 12:50:08"}, {"id":114970125, "gid": "O1R1DO", "cid":51503692, "gametime":19.56, "sent":4, "attack":9, "pcs":33, "players":2, "r1v1":0, "pos":2, "vs": "akatsuki16", "gtime": "2021-10-29 21:10:08"}, {"id":114970068, "gid": "K2RE1K", "cid":51503692, "gametime":52.96, "sent":39, "attack":46, "pcs":94, "players":2, "r1v1":0, "pos":1, "vs": "akatsuki16", "gtime": "2019-01-01 00:00:56"}]
    # test_list_of_dates = [i['gtime'] for i in test_list_of_games]
    # test_list_of_dates = [jstrishtml.datetime_to_str_naive(i) for i in test_list_of_dates]
    #
    # print(new_first_last_date(test_list_of_dates))
