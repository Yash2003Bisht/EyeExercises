# --------- built-in ---------
import os
import time
import json
import datetime
from typing import Any, Dict, Union, List
from json import JSONDecodeError

# --------- external ---------
import requests
import pyttsx3
import librosa
from mutagen.mp3 import MP3
from pygame import mixer
from requests.exceptions import ConnectionError, Timeout

# --------- internal ---------
# from reminders import *

ANSI_COLORS = [
    '\033[0;31m',  # red
    '\033[0;32m',  # green
    '\033[1;37m',  # white
]

exercise_start: bool = False


def text_to_speech(text: str, enabled: bool):
    """ Text to speech

    Args:
        text (str): text that function speak
        enabled (bool): feature enabled or not by the user
    """
    print(text)
    if enabled:
        engine: pyttsx3.engine.Engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


def play_sound(file: str, volume: float = 1.0):
    """ Play sounds

    Args:
        file (str): path of file to play music
        volume (float): volume
    """
    mixer.init()
    mixer_obj = mixer.music
    mixer_obj.set_volume(volume)
    mixer_obj.load(file)
    mixer_obj.play()


def toggle_exercise_start():
    """ Toggle exercise_start variable """
    global exercise_start
    exercise_start = False if exercise_start else True


def play_beep_sound(reminder_sound_path: str, beep_sound_path: str):
    """ Play a beep sound when no input is received from the user
    
    Args:
        reminder_sound_path (str): path of file to play music
        beep_sound_path (str): path of file to play beep
    """
    _, file_extension = os.path.splitext(reminder_sound_path)

    # duration of audio
    if file_extension == '.mp3':
        duration = MP3(reminder_sound_path).info.length
    elif file_extension == '.wav':
        duration = librosa.get_duration(filename=reminder_sound_path)
    else:
        print(f'{ANSI_COLORS[0]} Can\'t play beep sound because file format is not supported.'
              f' Only .mp3 and .wav are supported to calculate the total duration of reminder sound. {ANSI_COLORS[2]}')
        return None

    # don't play the beep sound while the exercise reminder sound is playing
    # sleep the program for those seconds
    time.sleep(duration)

    while True:
        # play beep sound after every 60 seconds
        time.sleep(60)
        if exercise_start:
            play_sound(beep_sound_path)
            continue
        break


def make_get_request(url: str, data=None) -> Union[Dict, None]:
    """ Makes a get request to the URL

    Args:
        url (str): URL to make a get reqeust
        data (Dict): category you like ex. news, tech, stock-market etc. Default is None

    Returns:
        Union[Dict, None]: return Dict if the request was made successfully otherwise None
    """
    if data is None:
        data = {}

    try:
        res = requests.get(url, data=json.dumps(data), timeout=30)
        if res.ok:
            response_data = res.json()
            return response_data["data"]
    except (Timeout, ConnectionError, JSONDecodeError):
        pass

    return None


def read_file(file_path: str, priority: int) -> Union[Dict, List]:
    """ Read config file data

    Args:
        file_path (str): path of the file
        priority (int): priority of the file

    Returns:
        Union[Dict, List]: can return a dictionary or list
    """
    # check the file exists or not
    if not os.path.exists(file_path):
        message: str = f'{ANSI_COLORS[0]} {file_path} not found'
        if priority == 1:
            message += f' can\'t run the program {ANSI_COLORS[2]}'
            print(message)
            quit()
        else:
            message += ANSI_COLORS[2]

        print(message)
        return []

    _, file_extension = os.path.splitext(file_path)

    with open(file_path) as file:
        if file_extension == '.json':
            data: Dict = json.load(file)
        else:
            data: List = list(filter(lambda x: len(x) > 0, file.read().split('\n')))

    return data


def catch_key_error(default_value: Any, data: Dict, *keys: Any):
    """ Searches for a value in a dictionary. If any key is not found returns the default_value.

    Args:
        default_value (Any): default value to be returned if any of the keys are not found in the dictionary.
        data (Dict): Dictionary to search for a value.
        *keys (Any): keys to search for a value. Multiple keys can be provided as separate arguments.
    """
    try:
        value: Any = None
        for key in keys:
            value = data[key]
        return value
    except (KeyError, TypeError):
        return default_value


def convert_to_datetime(date_string: str, specifier: str) -> Union[datetime.datetime, None]:
    """ Convert a given string representation of a date and time into a datetime object.

    Args:
        date_string (str): A string representing a date and time
        specifier (str): specifier to specify the datetime format

    Returns:
        Union[datetime.datetime, None]: A datetime object representing the converted date and time if the input
        string matches any of the supported formats, or None if no match is found.
    """
    formats = {
        "every": "%I:%M",              # ex. run it every 2 hours 15 minutes
        "daily": "%I:%M %p",           # ex. run it daily at 3:15 PM
        "on": "%d/%m/%Y",              # ex run it on 07/07/2023
        "on_at": "%d/%m/%Y %I:%M %p"   # ex run it on 30/08/2021 at 3:15 AM
    }

    try:
        datetime_obj = datetime.datetime.strptime(date_string, formats.get(specifier))
        return datetime_obj
    except (TypeError, ValueError):
        pass

    # return None if the string doesn't match any of the formats or specifier is not supported
    return None


def is_true(str_bool: str) -> bool:
    """Check if str_bool is True/False"""
    return str_bool.lower() == "true"
