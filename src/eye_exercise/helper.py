# --------- built-in ---------
import os
import time
import json
import datetime
import tempfile
from typing import Dict, Union, List
from json import JSONDecodeError

# --------- external ---------
import requests
import pyttsx3
import librosa
import pygame
from gtts import gTTS
from pydub import AudioSegment
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
        tts = gTTS(text=text, lang=lang)
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3")
        tts.save(temp_file.name)
        print(text)

        if no_speak_text:
            print(no_speak_text)

        # increased the volume of the generated speech
        audio = AudioSegment.from_file(temp_file.name, format="mp3")
        audio += volume  # ex. increase the volume by 6 dB
        audio.export(temp_file.name, format="mp3")

        # use a separate channel to play news audio file
        mixer.Channel(1).play(pygame.mixer.Sound(temp_file.name))
        while mixer.Channel(1).get_busy():
            pygame.time.Clock().tick(10)

    else:
        print(text)


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
