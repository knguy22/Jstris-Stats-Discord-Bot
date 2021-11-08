import requests
import time

# Returns all replay data of a username's specific gamemode
# game: 1 = sprint, 3 = cheese, 4 = survival, 5 = ultra, 7 = 20TSD, 8 = PC Mode
# mode: Sprint/Cheese: 1 = 40L/10L, 2 = 20L/18L, 3 = 100L, 4 = 1000L
#   for any other game, mode should be 1


class UserAllStats:
    all_stats = []
    data_criteria = {}
    page_request = ""
    username = ""
    game = ""
    mode = ""
    my_session = requests.session

    def __init__(self, username, game, mode='1'):
        self.username = username
        self.game = game
        self.mode = mode
        self.my_session = requests.session()
        self.all_stats = []

        self.data_criteria_init()

        self.username_all_replay_stats()

        self.duplicate_deleter()

        pass

    def data_criteria_init(self):
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
        # userleaderboard.txt is how all of the page's data will be stored
        time.sleep(1.5)
        r = self.my_session.get(url)
        self.page_request = r.text
        self.file_treater()

    def file_treater(self):

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
                        except:
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
                        except:
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
                return clock_to_seconds(timestring(self.page_request[lasttimeindex]))
            elif self.game == "5":
                return tdint(self.page_request[lasttimeindex])

    def page_200_replays_stats(self):

        # returns integers where there can be integers (Ex: blocks) and returns strings for others( Ex: date)

        # use the formatting of the time thing to find the line of the blocks, which is right after time taken;

        # uses <td><strong>, which is formatting for time, to find where all the other stats are in reference to each
        # timestamp on page

        # Example format on page (last - is a replay that has been deleted
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
                if "<td><strong>" in self.page_request[c-1]:
                    continue
                d = 1
                index = c - 2
                current_dict = {}
                for criteria in self.data_criteria:
                    if self.data_criteria[criteria] == 'userstring':
                        current_dict[criteria] = userstring(self.page_request[index])
                    elif self.data_criteria[criteria] == 'timestring':
                        current_dict[criteria] = timestring(self.page_request[index])
                    elif self.data_criteria[criteria] == 'string':
                        current_dict[criteria] = the_string(self.page_request[index])
                    elif self.data_criteria[criteria] == 'replaystring':
                        current_dict[criteria] = replaystring(self.page_request[index])
                    elif self.data_criteria[criteria] == 'tdint':
                        current_dict[criteria] = tdint(self.page_request[index])
                    elif self.data_criteria[criteria] == 'int':
                        current_dict[criteria] = my_int(self.page_request[index])
                    elif self.data_criteria[criteria] == 'float':
                        current_dict[criteria] = my_float(self.page_request[index])

                    if d == 1 or d == len(self.data_criteria) - 1:
                        index += 2
                    else:
                        index += 1
                    d += 1

                self.all_stats.append(current_dict)

    def username_all_replay_stats(self):

        isultra = False
        lines = None
        go_next_page = True
        gamemode = ''
        # converts game and mode to their respective strings to search in url
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
        elif self.game == "5":
            isultra = True
            gamemode = "ultra"
        elif self.game == "7":
            go_next_page = False
            gamemode = "20TSD"
        elif self.game == "8":
            go_next_page = False
            gamemode = "PC-mode"

        if not isultra:
            current_last_replay = "0"
        else:
            current_last_replay = "10000000000000000"

        while 1 == 1:

            # gets next page
            if lines and go_next_page:
                url = "https://jstris.jezevec10.com/{}?display=5&user={}&lines={}&page={}".format(
                    gamemode, self.username, lines, current_last_replay)
            elif lines is None and go_next_page:
                url = "https://jstris.jezevec10.com/{}?display=5&user={}&page={}".format(
                    gamemode, self.username, current_last_replay)
            else:
                url = "https://jstris.jezevec10.com/{}?display=5&user={}".format(
                    gamemode, self.username)

            self.username_leaderboard(url)

            # adds current page replays to list of all other replays so far
            self.page_200_replays_stats()

            # checks if there are no pages left
            if not self.check_200_replays():
                break

            if not go_next_page:
                break

            # sets up next url
            current_last_replay = str(self.last_time_in_page())

    def duplicate_deleter(self):
        c = 0
        while c < len(self.all_stats):
            if self.all_stats[c] == self.all_stats[c - 1]:
                self.all_stats.pop(c)
            c += 1


# Jstris html data conversions

def userstring(s):
    """

    Input:

        string: {}</a> where {} is username

    Output:

        string: username

    Ex:

        Input: streasure</a>
        Output: streasure

    """
    endindex = s.index("</a>")
    usernamestring = s[: endindex]
    return usernamestring


def timestring(s):

    """
    Input:

        string:
            <td><strong>1:47.<span class="time-mil">171</span></strong></td>

            example without any milliseconds:
                <td><strong>3:27</strong></td>

            example without minutes:
                <td><strong>2.798</strong></td>


    Output:

        float: time in seconds rounded to 3 digits

    """

    s = s.replace('<strong>', '')
    s = s.replace('</strong>', '')

    # check for minutes with the colon
    if ":" in s:
        minutes_beg = 4
        minutes_end = s.index(":")
        minutes = s[minutes_beg: minutes_end]
        has_minutes = True
    else:
        minutes = "0"
        has_minutes = False

    # check for milliseconds with '.'
    # time-mil only shows up if there are minutes

    if "." in s and has_minutes is True:
        milliseconds_beg = s.index("time-mil") + 10
        milliseconds_end = s.rindex("</span></td>")
        milliseconds = s[milliseconds_beg: milliseconds_end]
        while len(milliseconds) < 3:
            milliseconds += "0"
        has_milliseconds = True
    elif "." in s and has_minutes is False:
        milliseconds_beg = s.index(".") + 1
        milliseconds_end = s.rindex("</td>")
        milliseconds = s[milliseconds_beg: milliseconds_end]
        while len(milliseconds) < 3:
            milliseconds += "0"
        has_milliseconds = True
    else:
        milliseconds = "0"
        has_milliseconds = False

    # Guaranteed to have seconds
    # index where seconds begins and ends depends whether there are minutes and milliseconds

    if has_minutes:
        seconds_begin = s.index(":") + 1
    else:
        seconds_begin = 4
    if has_milliseconds:
        seconds_end = s.index(".")
    else:
        seconds_end = s.rindex("</td>")

    seconds = s[seconds_begin: seconds_end]

    if (minutes, seconds, milliseconds) == ('0', '-', '0'):
        return '-'
    if len(seconds) == 1:
        seconds = '0' + seconds

    return "{}:{}.{}".format(minutes, seconds, milliseconds)


def the_string(s):

    """
       Input:

           string
            Ex: <td>2020-08-11 18:06:53</td>


       Output:

           string:
           Ex: 2020-08-11 18:06:53

       """

    # example
    # <td>2020-08-11 18:06:53</td>

    s_end = s.rindex("</td>")
    s = s[4:s_end]
    return s


def replaystring(s):
    # example
    # <a href="https://jstris.jezevec10.com/replay/19483494" tar
    # get="_blank">(V3)<img src="https://jstris.jezevec10.com/res/play.png"></a>

    if "https://jstris.jezevec10.com/replay/" in s:
        s_end = s.index("target") - 2
        s = s[9:s_end]
    else:
        s = "-"
    return s


def tdint(s):
    # example
    # <td><strong>174,325</strong></td>

    s = s[s.index("<td><strong>") + 12: s.rindex("</strong></td>")]
    s = s.replace(",", "")

    return s


def my_int(s):
    # example line
    # <td>48</td>

    s_end = s.rindex("</td>")
    s = int(s[4:s_end])
    return s


def my_float(s):
    # example
    # <td>379.15</td>

    s_end = s.rindex("</td>")
    s = float(s[4:s_end])
    s = round(s, 2)
    return s


def clock_to_seconds(s):
    """
    Input:

        string: {a}:{b}.{c} where a = minutes, b = seconds, c = milliseconds rounded to 3 digits


    Output:

        float: time in seconds

    """
    # format
    # 1:43.365

    colonindex = s.index(":")
    periodindex = s.index(".")
    minutes = int(s[: colonindex])
    seconds = int(s[colonindex + 1: periodindex])
    milliseconds = float(s[periodindex:])

    return round(60 * minutes + seconds + milliseconds, 3)


if __name__ == "__main__":

    # Testing

    a1 = UserAllStats(username="riviclia", game='1', mode='1')
    print('1', a1.all_stats[0])
    b1 = UserAllStats(username="riviclia", game='1', mode='2')
    print('2', b1.all_stats[0])
    c1 = UserAllStats(username="riviclia", game='1', mode='3')
    print('3', c1.all_stats[0])
    d1 = UserAllStats(username="riviclia", game='1', mode='4')
    print('4', d1.all_stats[0])
    e = UserAllStats(username="riviclia", game='3', mode='1')
    print('5', e.all_stats[0])
    f = UserAllStats(username="riviclia", game='3', mode='2')
    print('6', f.all_stats[0])
    g = UserAllStats(username="riviclia", game='3', mode='3')
    print('7', g.all_stats[0])
    h = UserAllStats(username="riviclia", game='5', mode='1')
    print('8', h.all_stats[0])
    i = UserAllStats(username="riviclia", game='7', mode='1')
    print('9', i.all_stats[0])
    j = UserAllStats(username="riviclia", game='8', mode='1')
    print('10', j.all_stats[0])

    print(a1 == b1)
    print(b1 == c1)
    print(i == j)
    print(j == a1)
