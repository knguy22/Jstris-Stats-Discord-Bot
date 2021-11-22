import requests
import time

import jstrisfunctions
from jstrishtml import *
import datetime


# Returns all_stats containing entries of following dict:
# id, gid, cid, gametime, sent, attack, rep, pcs, players, r1v1, pos, vs, gtime, apm, spm, pps
# Ex: {"id":201211863,"gid":"MX2G04","cid":88899054,"gametime":71.31,"sent":81,
# "attack":94,"rep":"3","pcs":133,"players":4,"r1v1":0,"pos":1,"vs":"Torp","gtime":"2021-11-08 07:56:19"}

#  If username doesn't exist or there are no games, error will be logged into error_message

class UserLiveGames:

    def __init__(self, username, num_games=10000000000,
                 first_date="0001-01-01 00:00:00", last_date="9999-01-01 00:00:00"):
        """

        :param username: str
        :param num_games: int
        :param first_date: str
        :param last_date: str

        :return all_stats: (list)
                parameters from jstris api + (apm, spm, pps)

        """
        self.username: str = username
        self.num_games: int = num_games
        self.first_date: str = first_date
        self.last_date: str = last_date

        self.first_date = datetime.datetime.strptime(self.first_date, "%Y-%m-%d %H:%M:%S")
        self.last_date = datetime.datetime.strptime(self.last_date, "%Y-%m-%d %H:%M:%S")

        self.num_prev_dates = 5
        self.curr_date_and_prev_dates = list(range(self.num_prev_dates + 1))
        for i, j in enumerate(self.curr_date_and_prev_dates):
            self.curr_date_and_prev_dates[i] = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S") + datetime.\
                timedelta(days=i)
        self.prev_date_strike_num = 0
        self.potential_false_positive = 0
        self.in_time_period = False

        self.all_stats = []
        self.page_request = [{}]
        self.offset = 0
        self.still_searching = True
        self.has_error = False
        self.error_message = ""
        self.my_session = requests.session()

        self.check_username()
        if not self.has_error:
            self.username_games()
            self.check_has_games()
            if not self.has_error:
                self.first_last_date()

    def username_games(self):
        """

        iterates through jstris api games until all games are appended to dictionary
        """

        while self.still_searching is True:
            url = f"https://jstris.jezevec10.com/api/u/{self.username}/live/games?offset={self.offset}"
            self.username_leaderboard(url)
            self.append_stats()
            self.offset += 50

    def append_stats(self):

        """

        appends stats for current 50 replays in page; also checks if page is done yet if there are less than 50
        replays in page
        """
        for i, j in enumerate(self.page_request):

            # Dates can be None type for some reason; ignore these replays
            if j['gtime'] is None:
                continue

            if self.first_last_date_check(j):
                break

            if not self.in_time_period:
                continue

            # if current_date > self.last_date:
            #     self.in_time_period = False
            #     continue
            #
            # if self.prev_date_first_strike:
            #     print('first strike', self.curr_date_and_prev_dates, current_date, self.first_date, self.last_date)
            #     if current_date < self.first_date:
            #         self.still_searching = False
            #         break
            #     else:
            #         self.prev_date_first_strike = False
            #         self.all_stats.pop(-1)
            #
            # if current_date < self.first_date:
            #     if self.curr_date_and_prev_dates > current_date and not self.prev_date_first_strike:
            #         print('0 strike', self.curr_date_and_prev_dates, current_date)
            #         self.prev_date_first_strike = True

            # Adding apm, spm, pps and then appending to all stats

            j['apm'] = j['attack'] / j['gametime'] * 60
            j['spm'] = j['sent'] / j['gametime'] * 60
            j['pps'] = j['pcs'] / j['gametime']

            self.all_stats.append(j)

            # Checking for offset limit
            if self.num_games <= len(self.all_stats):
                self.still_searching = False
                break

    def first_last_date_check(self, j):
        # Update current_date and all previous dates
        self.curr_date_and_prev_dates.pop(-1)
        self.curr_date_and_prev_dates.insert(0, datetime.datetime.strptime(j['gtime'], "%Y-%m-%d %H:%M:%S"))

        # Check in time period; if so perhaps there is false positive
        if self.curr_date_and_prev_dates[0] <= self.last_date:
            self.in_time_period = True
            self.potential_false_positive += 1
        else:
            self.in_time_period = False

        if self.prev_date_strike_num > 0:
            if self.curr_date_and_prev_dates[0] < self.first_date\
                    and sorted(self.curr_date_and_prev_dates) == self.curr_date_and_prev_dates \
                    and self.prev_date_strike_num == self.num_prev_dates:
                print('strike success', self.curr_date_and_prev_dates, self.first_date, self.last_date)
                for m in range(self.num_prev_dates):
                    self.all_stats.pop(-1)
                    if len(self.all_stats) == 0:
                        break
                self.still_searching = False
                return True

            elif self.prev_date_strike_num == self.num_prev_dates:
                # print('strike fail', self.curr_date_and_prev_dates, self.first_date, self.last_date, self.in_time_period)
                self.prev_date_strike_num = 0
                if not self.in_time_period:
                    for n in range(self.potential_false_positive):
                        self.all_stats.pop(-1)
                self.potential_false_positive = 0

            else:
                # print('checking strike', self.curr_date_and_prev_dates)
                self.prev_date_strike_num += 1

        if self.curr_date_and_prev_dates[0] < self.first_date:
            if self.curr_date_and_prev_dates[1] > self.curr_date_and_prev_dates[0] and not self.prev_date_strike_num:
                self.prev_date_strike_num = 1

    def username_leaderboard(self, url):
        """

        Stores a url's data into self.page_request
        """
        # print(url)
        r = self.my_session.get(url)
        self.page_request = r.json()
        time.sleep(1)
        if len(self.page_request) < 50:
            self.still_searching = False

    def check_username(self):
        my_url = f"https://jstris.jezevec10.com/api/u/{self.username}/live/games?offset=0"
        r = self.my_session.get(my_url)
        self.page_request = r.json()
        time.sleep(1)
        if "error" in self.page_request:
            self.has_error = True
            self.error_message = f"{self.username}: Not valid username"

    def check_has_games(self):
        if len(self.all_stats) == 0:
            self.has_error = True
            self.error_message = f"{self.username}: No played games"

    def first_last_date(self):

        if datetime.datetime.strptime(self.all_stats[-1]['gtime'], "%Y-%m-%d %H:%M:%S") < self.first_date:
            self.all_stats.pop(-1)

        min_time = self.all_stats[-1]["gtime"]
        max_time = self.all_stats[1]["gtime"]

        self.first_date = str(min_time)
        self.last_date = str(max_time)

# Returns all replay data of a username's specific gamemode
# game: 1 = sprint, 3 = cheese, 4 = survival, 5 = ultra, 7 = 20TSD, 8 = PC Mode
# mode: Sprint/Cheese: 1 = 40L/10L, 2 = 20L/18L, 3 = 100L, 4 = 1000L
#       for any other game, mode should be 1
#
#  Each dictionary contains replay data of a single replay
#  See data_criteria_init for the entries of the dict
#
#  If username doesn't exist or there are no games, error will be logged into error_message


class UserIndivGames:

    def __init__(self, username, game, mode='1', period='0'):

        """

        :param username: str
        :param game: str of int
        :param mode: str of int
        :param period: str of int

        Ex: username = Truebulge, game = 1, mode = 1, period = 0

        :return allstats: list
            List of dictionaries ordered by time (least to most time)
            Each dictionary contains replay data of a single replay
            See data_criteria_init for the entries of the dict

        """

        self.username: str = username
        self.game: str = game
        self.mode: str = mode
        self.period: str = period

        self.all_stats = []
        self.my_session = requests.session()
        self.page_request = ""
        self.current_last_replay = ""
        self.has_error = False
        self.error_message = ""
        self.data_criteria = {}

        self.check_username()

        if self.has_error is False:
            self.data_criteria_init()
            self.username_all_replay_stats()
            self.duplicate_deleter()
            self.check_has_games()

    def username_all_replay_stats(self):
        """
        :return:
        """
        is_ultra_or_survival = False
        lines = None
        is_20tsd_or_pcmode = False
        gamemode = ''

        # converts game and mode to their respective strings to search in url
        # also checks which url format to search for
        if self.game == "1":
            gamemode = "sprint"
            if self.mode == "2":
                lines = "20L"
            elif self.mode == "1":
                lines = "40L"
            elif self.mode == "3":
                lines = "100L"
            elif self.mode == "4":
                lines = "1000L"
        elif self.game == "3":
            gamemode = "cheese"
            if self.mode == "1":
                lines = "10L"
            elif self.mode == "2":
                lines = "18L"
            elif self.mode == "3":
                lines = "100L"
        elif self.game == "4":
            gamemode = "survival"
            is_ultra_or_survival = True
        elif self.game == "5":
            is_ultra_or_survival = True
            gamemode = "ultra"
        elif self.game == "7":
            is_20tsd_or_pcmode = True
            gamemode = "20TSD"
        elif self.game == "8":
            is_20tsd_or_pcmode = True
            gamemode = "PC-mode"

        if not is_ultra_or_survival:
            self.current_last_replay = "0"
        else:
            self.current_last_replay = "10000000000000000"

        while 1 == 1:

            # gets next page
            if lines and not is_20tsd_or_pcmode:
                url = f"https://jstris.jezevec10.com/{gamemode}?display=5&user={self.username}&lines={lines}" \
                      f"&page={self.current_last_replay}&time={self.period}"
            elif lines is None and not is_20tsd_or_pcmode:
                url = f"https://jstris.jezevec10.com/{gamemode}?display=5&user={self.username}" \
                      f"&page={self.current_last_replay}&time={self.period}"
            else:
                url = f"https://jstris.jezevec10.com/{gamemode}?display=5&user={self.username}&time={self.period}"

            self.username_leaderboard(url)

            # adds current page replays to list of all other replays so far
            self.page_200_replays_stats()

            # checks if there are no pages left by checking if there are less than 200 replays in current page
            if not self.check_200_replays():
                break

            # 20tsd and pcmode only store first 200 replays
            if is_20tsd_or_pcmode:
                break

            # sets up next url
            self.current_last_replay = str(self.last_time_in_page())

    def page_200_replays_stats(self):

        # returns integers where there can be integers (Ex: blocks) and returns strings for others( Ex: date)

        # use the formatting of the time thing to find the line of the blocks, which is right after time taken;

        # uses <td><strong>, which is formatting for time, to find where all the other stats are in reference to each
        # timestamp on page

        # Example format on page (last - is a replay that has been deleted)
        # streasure</a>
        # </td>
        # <td><strong>288:57.<span class="time-mil">800</span></strong></td>
        # <td>1167</td>
        # <td>0.07</td>
        # <td>1542</td>
        # <td>2021-01-07 01:23:52</td>
        # <td>
        # -

        c = -1
        while len(self.page_request) - 1 > c:
            c += 1
            if "<td><strong>" in self.page_request[c]:
                if "<td><strong>" in self.page_request[c - 1]:
                    continue
                d = 1
                index = c - 2
                current_dict = {}
                for criteria in self.data_criteria:
                    if self.data_criteria[criteria] == 'userstring':
                        current_dict[criteria] = user_string(self.page_request[index])
                    elif self.data_criteria[criteria] == 'timestring':
                        current_dict[criteria] = time_string(self.page_request[index])
                    elif self.data_criteria[criteria] == 'string':
                        current_dict[criteria] = date_string(self.page_request[index])
                    elif self.data_criteria[criteria] == 'replaystring':
                        current_dict[criteria] = replay_string(self.page_request[index])
                    elif self.data_criteria[criteria] == 'tdint':
                        current_dict[criteria] = td_int(self.page_request[index])
                    elif self.data_criteria[criteria] == 'int':
                        current_dict[criteria] = my_int(self.page_request[index])
                    elif self.data_criteria[criteria] == 'float':
                        current_dict[criteria] = my_float(self.page_request[index])

                    if d == 1 or d == len(self.data_criteria) - 1:
                        index += 2
                    else:
                        index += 1
                    d += 1

                old_dict = current_dict
                current_dict = {}
                for i in old_dict:
                    if i != "date":
                        current_dict[i] = old_dict[i]
                    else:
                        current_dict["date (CET)"] = old_dict[i]
                self.all_stats.append(current_dict)

    def check_has_games(self):
        if len(self.all_stats) == 0:
            self.has_error = True
            self.error_message = f"{self.username}: No played games"

    def check_username(self):
        my_url = f"https://jstris.jezevec10.com/u/{self.username}"
        self.username_leaderboard(url=my_url)
        if "<p>Requested link is invalid.</p>" in self.page_request:
            self.has_error = True
            self.error_message = f"{self.username}: Not valid username"

    def data_criteria_init(self):

        """

        :return: data_criteria: all of the different stats from each replay
        """

        if self.game in ('1', '3', '4'):
            self.data_criteria = {"username": "userstring", "time": "timestring",
                                  "blocks": "int", "pps": "float", "finesse": "int",
                                  "date": "string", "replay": "replaystring"}
        elif self.game == '5':
            self.data_criteria = {"username": "userstring", "score": "tdint",
                                  "blocks": "int", "ppb": "float", "pps": "float", "finesse": "int",
                                  "date": "string", "replay": "replaystring"}
        elif self.game == '7':
            self.data_criteria = {"username": "userstring", "tsds": "tdint", "time": "timestring",
                                  "20tsd time": "timestring", "blocks": "int", "pps": "float", "date": "string",
                                  "replay": "replaystring"}

        elif self.game == '8':
            self.data_criteria = {"username": "userstring", "pcs": "tdint", "clock": "clockstring",
                                  "blocks": "int", "pps": "float", "finesse": "int",
                                  "date": "string", "replay": "replaystring"}

    def username_leaderboard(self, url):
        """

        Stores a url's data into self.page_request
        """

        print(url)
        r = self.my_session.get(url)
        self.page_request = r.text
        self.file_treater()
        time.sleep(1.5)

    def file_treater(self):

        """
        Handles any page requests fuckery like empty lines and spaces before each line
        """

        self.page_request = self.page_request.splitlines()
        c = 0
        total_indices = len(self.page_request)
        while total_indices - c > 0:
            if len(self.page_request[c]) == 0:
                self.page_request.pop(c)
                total_indices -= 1
                c -= 1
            if self.page_request[c][0] == ' ':
                self.page_request[c] = self.page_request[c][1:]
            c += 1

    def check_200_replays(self):

        """

        Checks if there are 200 replays on current page
        """

        first_replay = 0
        last_replay = 0

        checking_first_replay = True

        c = 0
        # Getting the first number of the replay (like 1st place) and last number
        while len(self.page_request) - c > 0:
            d = 0
            if "<td><strong>" in self.page_request[c]:
                if checking_first_replay:
                    while 1 == 1:
                        try:
                            int(self.page_request[c - d])
                        except ValueError:
                            pass
                        else:
                            first_replay = int(self.page_request[c - d])
                            break
                        d += 1
                    checking_first_replay = False
                else:
                    while 1 == 1:
                        try:
                            int(self.page_request[c - d])
                        except ValueError:
                            pass
                        else:
                            last_replay = int(self.page_request[c - d])
                            break
                        d += 1
            c += 1

        if last_replay - first_replay == 199:
            return True

        return False

    def last_time_in_page(self):

        """
        :return last time in seconds or score in points of the page
        """

        # returns integers
        # set up stuff, get the file from user_leaderboard_file

        c = 0
        lasttimeindex = 0

        # only the time uses this format

        while len(self.page_request) - c > 0:
            if "<td><strong>" in self.page_request[c]:
                lasttimeindex = c
            c += 1

        if lasttimeindex == 0:
            return 0
        else:
            if self.game != "5":
                return clock_to_seconds(time_string(self.page_request[lasttimeindex]))
            elif self.game == "5":
                return td_int(self.page_request[lasttimeindex])

    def duplicate_deleter(self):
        """

        :return: all_stats with duplicate replays deleted
        """

        if len(self.all_stats) == 1:
            return None

        c = 0
        while c < len(self.all_stats):
            if self.all_stats[c] == self.all_stats[c - 1]:
                self.all_stats.pop(c)
                c -= 1
            c += 1


if __name__ == "__main__":
    h = UserLiveGames("sio", num_games=200000)
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)

    h = UserLiveGames("reminder", num_games=200000)
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)

    h = UserLiveGames("zebrahugger", num_games=200000, first_date="2021-03-15 00:00:00", last_date="2021-09-30 00:00:00")
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)

    h = UserLiveGames("quickandsmart", num_games=200000, first_date="2021-03-15 00:00:00", last_date="2021-09-30 00:00:00")
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)

    h = UserLiveGames("cloak", num_games=200000, first_date="2021-07-25 06:07:01", last_date="2021-07-25 06:26:43")
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)

    h = UserLiveGames("vince_hd", num_games=200000, first_date="2021-07-25 06:07:01", last_date="2021-07-25 06:26:43")
    print(h.username)
    print(h.first_date, h.last_date)
    print(len(h.all_stats))
    a = jstrisfunctions.opponents_matchups(h.all_stats)
    print(a)
    # h = UserLiveGames("reminder", num_games=200000, first_date="2021-11-21 00:00:00", last_date="2021-11-21 00:00:00")
