import requests
import time
import jstris_stats

# Deals with all my formatting nonsense in unorderedstats.txt
# Does not support ultra runs and other stuff yet

# class user_stats:
#
#     def unordered_username(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         usernameindex = 0
#         timeindex = statstring.index("Time: ")
#         final_username = statstring[usernameindex: timeindex - 2]
#
#         return final_username
#
#     def unordered_time(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         timeindex = statstring.index("Time: ")
#         blocksindex = statstring.index("Blocks: ")
#         final_time = statstring[timeindex + 6: blocksindex - 2]
#
#         return final_time
#
#     def unordered_block(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         blocksindex = statstring.index("Blocks: ")
#         ppsindex = statstring.index("PPS: ")
#         final_block = int(statstring[blocksindex + 8: ppsindex - 2])
#
#         return final_block
#
#     def unordered_pps(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         ppsindex = statstring.index("PPS: ")
#         finesseindex = statstring.index("Finesse: ")
#         final_pps = float(statstring[ppsindex + 5: finesseindex - 2])
#
#         return final_pps
#
#     def unordered_finesse(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         finesseindex = statstring.index("Finesse: ")
#         dateindex = statstring.index("Date: ")
#         final_finesse = int(statstring[finesseindex + 9: dateindex - 2])
#
#         return final_finesse
#
#     def unordered_date(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         dateindex = statstring.index("Date: ")
#         linkindex = statstring.index("Link: ")
#         final_date = statstring[dateindex + 6: linkindex - 2]
#
#         return final_date
#
#     def unordered_link(statstring):
#         # format:
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#
#         linkindex = statstring.index("Link: ")
#         final_link = statstring[linkindex + 6: ]
#
#         return final_link
#
#     def unordered_clock_to_seconds(timestring):
#         return jstris_stats.clock_to_seconds(user_stats.unordered_time(timestring))
#
#     def statsstring_to_dict(statsstring):
#         # format
#         # Vince_HD  Time: 1:43.365  Blocks: 240  PPS: 2.32  Finesse: 9  Date: 2020-03-12 08:27:26  Link: https://jstris.jezevec10.com/replay/12611720
#         my_dict = {}
#         my_dict['username'] = user_stats.unordered_username(statsstring)
#         my_dict['time'] = user_stats.unordered_username(statsstring)
#         my_dict['block'] = user_stats.unordered_username(statsstring)
#         my_dict['pps'] = user_stats.unordered_username(statsstring)
#         my_dict['finesse'] = user_stats.unordered_username(statsstring)
#         my_dict['date'] = user_stats.unordered_username(statsstring)
#         my_dict['link'] = user_stats.unordered_username(statsstring)
#
#
#         return my_dict

class user_all_stats:
    all_stats = []
    data_criteria = {}
    page_request = ""

    def __init__(self, username, game, mode):
        my_session = requests.session()
        self.all_stats = self.username_all_replay_stats(username, game, mode, my_session)
        pass

    def username_leaderboard_file(self ,url, my_session=False):
        time.sleep(1.5)
        # userleaderboard.txt is how all of the page's data will be stored

        if my_session is False:
            r = requests.get(url)
        else:
            r = my_session.get(url)

        # with open(file_output, "w", encoding="utf-8") as filename:
        #     filename.write(r.text)
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
                if checking_first_replay == True:
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

    def last_time_in_page(self, game):

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
            if game != "5":
                return jstris_stats.time(self.page_request[lasttimeindex])
            elif game == "5":
                return jstris_stats.score(self.page_request[lasttimeindex])

    def page_200_replays_stats(self):

        # returns integers where there can be integers (Ex: blocks) and returns strings for others( Ex: date)

        allstats = []

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

        c = 0
        while len(self.page_request) - c > 0:

            if "<td><strong>" in self.page_request[c]:
                currentusername = self.page_request[c - 2]
                currentusername = jstris_stats.username(currentusername)

                currenttime = self.page_request[c]
                currenttime = jstris_stats.time(currenttime)

                currentblock = self.page_request[c + 1]
                currentblock = jstris_stats.blocks(currentblock)

                currentpps = self.page_request[c + 2]
                currentpps = jstris_stats.pps(currentpps)

                currentfinesse = self.page_request[c + 3]
                currentfinesse = jstris_stats.finesse(currentfinesse)

                currentdate = self.page_request[c + 4]
                currentdate = jstris_stats.date(currentdate)

                currentlink = self.page_request[c + 6]
                currentlink = jstris_stats.link(currentlink)

                allstats.append(
                    (currentusername, currenttime, currentblock, currentpps, currentfinesse, currentdate,
                     currentlink))
            c += 1

        return allstats

    def username_all_replay_stats(self, username, game, mode, my_session=False):
        current_last_replay = "0"
        allpagesstats = []

        # converts game and mode to their respective strings to search in url
        if game == "1":
            gamemode = "sprint"
            if mode == "2":
                lines = "20L"
            elif mode == "1":
                lines = "40L"
            elif mode == "3":
                lines = "100L"
            elif mode == "4":
                lines = "1000L"
            else:
                "invalid mode"
                return -69
        elif game == "3":
            gamemode = "cheese"
            if mode == "1":
                lines = "10L"
            elif mode == "2":
                lines = "18L"
            elif mode == "3":
                lines = "100L"
        elif game == "4":
            gamemode = "survival"
        elif game == "5":
            gamemode = "ultra"

        while 1 == 1:

            # gets next page
            url = "https://jstris.jezevec10.com/" + gamemode + "?display=5&user=" + username + "&lines=" + lines + "&page=" + current_last_replay
            self.username_leaderboard_file(url)

            # adds current page replays to list of all other replays so far
            allpagesstats.extend(self.page_200_replays_stats())

            # checks if there are no pages left
            if self.check_200_replays() == False:
                break

            # sets up next url
            current_last_replay = str(self.last_time_in_page(game))

        return allpagesstats

