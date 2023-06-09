# --------- built-in ---------
import datetime
from typing import List

# --------- internal ---------
from helper import read_file, convert_to_datetime


def check_reminders(reminder_file_path: str) -> None:
    """ Checks the reminders file.

    Args:
        reminder_file_path (str): reminder file path
    """
    reminders: List[str] = read_file(reminder_file_path, 0)
    for remind in reminders:
        date_time, func = remind.split(" - ")
        date_time, current_datetime = convert_to_datetime(date_time), datetime.datetime.now()
        print(date_time, current_datetime, func)
        # if (current_datetime - date_time).seconds
