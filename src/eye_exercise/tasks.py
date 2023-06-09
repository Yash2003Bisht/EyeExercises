# --------- built-in ---------
import os
import tempfile
from typing import Union, Dict

# --------- external ---------
import pygame
from gtts import gTTS
from pydub import AudioSegment
from pygame import mixer

# --------- internal ---------
from eye_exercise.helper import make_get_request


def google_text_to_speech(text: str, enabled: bool, volume: int, lang: str = "hi"):
    """ Google text to speech

    Args:
        text (str): text that function speak
        enabled (bool): feature enabled or not by the user
        volume (int): volume of gtts
        lang (str): language
    """
    if enabled:
        tts = gTTS(text=text, lang=lang)
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3")
        tts.save(temp_file.name)
        print(text)

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


def get_headline(ip_address: str, category: str) -> Union[Dict, None]:
    """ Makes a get request to news scraper headline endpoint.

    Args:
        ip_address (str): IP address of server
        category (str): category you like ex. news, tech, stock-market etc.

    Returns:
        Union[Dict, None]: return Dict if the request was made successfully otherwise None
    """
    url = "http://" + os.path.join(ip_address, "headline")
    data = {"category": category}
    return make_get_request(url, data)
