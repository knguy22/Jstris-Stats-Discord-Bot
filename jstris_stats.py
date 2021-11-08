
# Interprets html to txt formatting to get the stats we want
# Everything below will return an integer/float except for the date, link and timestring, which return a string

def username(usernamestring: str) -> str:
    """

    Input:

        string: {}</a> where {} is username

    Output:

        string: username

    Ex:

        Input: streasure</a>
        Output: streasure

    """

    endindex = usernamestring.index("</a>")
    usernamestring = usernamestring[: endindex]
    return usernamestring


# jstris time format to seconds

def time(timestring: str) -> float:

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

    # Use this because somethings there is a space before <td><strong> for no apparent reason
    timestringbeginning = timestring.index("<td><strong>")

    # check for minutes with the colon
    if ":" in timestring:
        minutesbeg = timestringbeginning + 12
        minutesend = timestring.index(":")
        minutes = timestring[minutesbeg: minutesend]
        hasminutes = True
    else:
        minutes = "0"
        hasminutes = False

    # check for milliseconds with '.'
    # time-mil only shows up if there are minutes

    if "." in timestring and hasminutes is True:
        millisecondsbeg = timestring.index("time-mil") + 10
        millisecondsend = timestring.rindex("</span></strong></td>")
        milliseconds = timestring[millisecondsbeg: millisecondsend]
        while len(milliseconds) < 3:
            milliseconds += "0"
        hasmilliseconds = True
    elif "." in timestring and hasminutes is False:
        millisecondsbeg = timestring.index(".") + 1
        millisecondsend = timestring.rindex("</strong></td>")
        milliseconds = timestring[millisecondsbeg: millisecondsend]
        while len(milliseconds) < 3:
            milliseconds += "0"
        hasmilliseconds = True
    else:
        milliseconds = "0"
        hasmilliseconds = False

    # Guaranteed to have seconds
    # index where seconds begins and ends depends whether there are minutes and milliseconds

    if hasminutes:
        secondsbegin = timestring.index(":") + 1
    else:
        secondsbegin = timestringbeginning + 12
    if hasmilliseconds:
        secondsend = timestring.index(".")
    else:
        secondsend = timestring.rindex("</strong></td>")

    seconds = timestring[secondsbegin: secondsend]

    return 60 * int(minutes) + int(seconds) + 0.001 * int(milliseconds)


# seconds to clock format
def seconds_to_clock(timefloat: float) -> str:
    """
    Input:

        float: time in seconds


    Output:

        string: {a}:{b}.{c} where a = minutes, b = seconds, c = milliseconds rounded to 3 digits

    """

    minutes = int(timefloat // 60)
    seconds = int(timefloat - 60 * minutes // 1)
    milliseconds = round(timefloat - (60 * minutes) - seconds, 3)

    minutes = str(minutes)
    # deals with seconds when it's below 10 like 1:06
    if seconds < 10:
        seconds = "0" + str(seconds)
    else:
        seconds = str(seconds)
    milliseconds = str(milliseconds)

    timestring = minutes + ":" + seconds + "." + milliseconds[2:]
    return timestring


# clock to seconds format
def clock_to_seconds(timestring):
    """
    Input:

        string: {a}:{b}.{c} where a = minutes, b = seconds, c = milliseconds rounded to 3 digits


    Output:

        float: time in seconds

    """
    # format
    # 1:43.365

    colonindex = timestring.index(":")
    periodindex = timestring.index(".")
    minutes = int(timestring[: colonindex])
    seconds = int(timestring[colonindex + 1: periodindex])
    milliseconds = float(timestring[periodindex:])

    return round(60 * minutes + seconds + milliseconds, 3)


def blocks(blocksstring: str) -> int:

    """
    Input:

        string: <td>{a}</td> where a = number of blocks


    Output:

        int: number of blocks

    """

    # example line
    # <td>236</td>

    blockstringend = blocksstring.rindex("</td>")
    blocksstring = int(blocksstring[4:blockstringend])
    return blocksstring


def pps(ppsstring: str) -> float:
    """
       Input:

           string: <td>{a}</td> where a = pps


       Output:

           float: pps

       """

    # example line
    # <td>0.08</td>

    ppsstringend = ppsstring.rindex("</td>")
    ppsstring = float(ppsstring[4:ppsstringend])
    ppsstring = round(ppsstring, 2)
    return ppsstring


def finesse(finessestring: str) -> int:
    """
       Input:

           string: <td>{a}</td> where a = finesse


       Output:

           int: finesse

       """

    # example line
    # <td>48</td>

    finessestringend = finessestring.rindex("</td>")
    finessestring = int(finessestring[4:finessestringend])
    return finessestring


def date(datestring: str) -> str:

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

    datestringend = datestring.rindex("</td>")
    datestring = datestring[4:datestringend]
    return datestring


def link(linkstring: str) -> str:
    # example
    # <a href="https://jstris.jezevec10.com/replay/19483494" tar
    # get="_blank">(V3)<img src="https://jstris.jezevec10.com/res/play.png"></a>

    if "https://jstris.jezevec10.com/replay/" in linkstring:
        linkstringend = linkstring.index("target") - 2
        linkstring = linkstring[9:linkstringend]
    else:
        linkstring = "-"
    return linkstring


def score(scorestring: str) -> str:
    # example
    # <td><strong>174,325</strong></td>

    scorestring = scorestring[scorestring.index("<td><strong>") + 12: scorestring.rindex("</strong></td>")]
    scorestring = scorestring.replace(",", "")

    return scorestring


def ppb(ppbstring: str) -> float:
    # example
    # <td>379.15</td>

    ppbstringend = ppbstring.rindex("</td>")
    ppbstring = float(ppbstring[4:ppbstringend])
    ppbstring = round(ppbstring, 2)
    return ppbstring

# TO DO:
# ADD PCS