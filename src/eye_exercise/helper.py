# --------- built-in ---------
import os
import json
import datetime
import tempfile
from typing import Dict, Union, List
from json import JSONDecodeError

# --------- external ---------
import requests
import pyttsx3
import pygame
from gtts import gTTS
from pydub import AudioSegment
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
exercise_paused: bool = False


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


def toggle_exercise_start(required_value: bool = False) -> None | bool:
    """ Toggle exercise_start variable """
    global exercise_start

    if not required_value:
        exercise_start = False if exercise_start else True
    else:
        return exercise_start


def toggle_exercise_paused(required_value: bool = False) -> None | bool:
    """ Toggle exercise_paused variable """
    global exercise_paused

    if not required_value:
        exercise_paused = False if exercise_paused else True
    else:
        return exercise_paused


def make_get_request(url: str, data: Dict = None, timeout: int = 30) -> Union[Dict, None]:
    """ Makes a get request to the URL

    Args:
        url (str): URL to make get reqeust
        data (Dict): category you like i.e. news, tech, stock-market etc. Default is None
        timeout (int): specifies the number of seconds the waits getting a response. Default is 30

    Returns:
        Union[Dict, None]: return Dict if the request was made successfully otherwise None
    """
    if data is None:
        data = {}

    try:
        res = requests.get(url, data=json.dumps(data), timeout=timeout)
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


def store_logs(file_name: str, path: str, log: str, extension: str = "log"):
    """ Use this function to store the logs to a text file

    Args:
        file_name (str): Name of the file
        path (str): Path to store the file
        extension (str): File extension, default is .logs
        log (str): Log to store
    """
    file_name = f"{file_name}.{extension}"
    full_path = os.path.join(path, file_name)

    # create the directory if not exists
    if not os.path.exists(path):
        os.mkdir(path)

    with open(full_path, "a") as file:
        file.write(log)


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


def google_text_to_speech(text: str, enabled: bool, volume: int, lang: str = "hi", no_speak_text: str = None):
    """ Google text to speech

    Args:
        text (str): text that function speaks
        enabled (bool): feature enabled or not by the user
        volume (int): volume of gtts
        lang (str): language
        no_speak_text (str): Any additional information just want to print it
    """
    if enabled:
        try:
            tts = gTTS(text=text, lang=lang)
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3")
            tts.save(temp_file.name)
            print(text)

            if no_speak_text:
                print(no_speak_text)

            # store the news logs to a file
            news_log = f"{text}\n{no_speak_text}\n\n"
            store_logs("news_logs", "logs", news_log)

            # increased the volume of the generated speech
            audio = AudioSegment.from_file(temp_file.name, format="mp3")
            audio += volume  # ex. increase the volume by 6 dB
            audio.export(temp_file.name, format="mp3")

            # use a separate channel to play news audio file
            # initialize the mixer
            mixer.init()
            mixer.Channel(1).play(mixer.Sound(temp_file.name))
            while mixer.Channel(1).get_busy():
                pygame.time.Clock().tick(10)

        # catch the exception
        except Exception as err:
            # log the error and pass the text to text_to_speech
            print(err)
            text_to_speech(text, enabled)

    else:
        print(text)
        print(no_speak_text)
        text_to_speech(f"{int(os.environ['exercise_time']) // 2} seconds passed",
                       is_true(os.environ.get("text_to_speech_enabled", "true")))


def get_headline(ip_address: str, category: str, delay: int) -> Union[Dict, None]:
    """ Makes a get request to news scraper headline endpoint.

    Args:
        ip_address (str): IP address of server
        category (str): category you like i.e news, tech, stock-market etc.
        delay (int): exercise time in seconds

    Returns:
        Union[Dict, None]: return Dict if the request was made successfully otherwise None
    """
    url = "http://" + os.path.join(ip_address, "headline")
    data = {"category": category}
    timeout = delay // 2
    return make_get_request(url, data, timeout)


def load_env(env_path: str = None) -> None:
    """ Load the env files

    Args:
        env_path (str): Path of the env file default is None
    """
    if env_path:
        path = env_path
    else:
        path = ".env"

    with open(path) as env:
        for data in env.readlines():
            data = data.replace("\n", "")
            if data and not data.startswith("#"):
                key, value = data.split("=", 1)
                os.environ[key] = value


def is_true(str_bool: str) -> bool:
    """Check if str_bool is True/False"""
    return str_bool.lower() == "true"
