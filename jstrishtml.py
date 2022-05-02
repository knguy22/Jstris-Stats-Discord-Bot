# Jstris html data conversions


def user_string(s: str) -> str:
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


def time_string(s: str) -> str:

    """
    Input:
        string:
            <td><strong>1:47.<span class="time-mil">171</span></strong></td>
            example without any milliseconds:
                <td><strong>3:27</strong></td>
            example without minutes:
                <td><strong>2.798</strong></td>
    Output:
        string: time in clock format
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

    return f"{minutes}:{seconds}.{milliseconds}"


def date_string(s: str) -> str:

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


def replay_string(s: str) -> str:

    """
       Input:
           string
            Ex: <a href="https://jstris.jezevec10.com/replay/19483494" target=
            "_blank">(V3)<img src="https://jstris.jezevec10.com/res/play.png"></a>
       Output:
           string:
           Ex: https://jstris.jezevec10.com/replay/19483494
       """

    if "https://jstris.jezevec10.com/replay/" in s:
        s_end = s.index("target") - 2
        s = s[9:s_end]
    else:
        s = "-"
    return s + " "


def td_int(s: str) -> int:
    # example
    # <td><strong>174,325</strong></td>
    """

    :param s: string
            example: <td><strong>174,325</strong></td>
    :return: string of int
            example: 174325
    """

    s = s[s.index("<td><strong>") + 12: s.rindex("</strong></td>")]
    s = s.replace(",", "")

    return int(s)


def my_int(s: str) -> int:
    """

    :param s: string
            example: <td>48</td>
    :return: int
            example: 48
    """

    s_end = s.rindex("</td>")
    s = int(s[4:s_end])
    return s


def my_float(s: str) -> float:
    # example
    # <td>379.15</td>
    """

    :param s: string
            example: <td>379.15</td>
    :return: float
            example: 379.15
    """

    s_end = s.rindex("</td>")
    s = float(s[4:s_end])
    return round(s, 2)

if __name__ == "__main__":
    pass
