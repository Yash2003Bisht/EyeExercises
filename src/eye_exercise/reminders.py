# --------- built-in ---------
from typing import Union, Dict, List, Tuple

# --------- external ---------
from tabulate import tabulate

# --------- internal ---------
from eye_exercise.helper import *


def get_market_stats(ip_address: str, exchange: str) -> Union[None, Dict]:
    """ Returns the stock market stats

    Args:
        ip_address (str): IP address of the server
        exchange (str): exchange NSE or BSE

    Returns:
        Union[None, Dict]: Returns a dict if the request was made successfully otherwise None
    """
    url = "http://" + os.path.join(ip_address, "market-stats")
    data = {"exchange": exchange}
    return make_get_request(url, data)


def stdout_market_stats(ip_address: str, exchange: str):
    market_stats: Dict = get_market_stats(ip_address, exchange)
    text_to_speech("Today's Market Stats", True)
    for stats in market_stats:
        print(f"==================== {stats.upper()} ====================")
        print(tabulate(market_stats[stats], headers='firstrow', tablefmt='fancy_grid'), end="\n\n")


def check_reminders(reminder_file_path: str, exercise_interval_time: int) -> Tuple[bool, Dict]:
    """ Checks the reminders file and run the function.

    Args:
        reminder_file_path (str): reminder file path
        exercise_interval_time (int): exercise interval time

    Returns:
        Tuple[bool, Dict]: True and a dict if the reminder condition is true otherwise False and empty dict
    """
    reminders: List[str] = read_file(reminder_file_path, 0)

    for remind in reminders:
        specifier, reminder_datetime, func_to_exec, args = map(lambda text: text.lower(), remind.split(" - "))
        reminder_datetime, current_datetime = convert_to_datetime(reminder_datetime, specifier), \
            datetime.datetime.now()

        # change the year, month & day if reminder specifier is set as "every" or "daily"
        if specifier in ["every", "daily"]:
            reminder_datetime = reminder_datetime.replace(year=current_datetime.year, month=current_datetime.month,
                                                          day=current_datetime.day)

        # check the reminder and current datetime
        diff: float = (reminder_datetime - current_datetime).total_seconds()
        if 0 < diff < exercise_interval_time / 1.5 or exercise_interval_time * 0.5 - abs(diff) > 0:
            return True, {"func": func_to_exec, "args": args.split(" ")}

    return False, {}


if __name__ == "__main__":
    check_reminders("../text_files/reminders.txt", 600)
