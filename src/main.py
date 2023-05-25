"""
@author: Yash Bisht
@date: 02/10/2022
@description: Eye Exercise Reminder
"""

# --------- built-in ---------
import os
import json
import random
import time
import datetime
import math
from threading import Thread

# hide the pygame message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# --------- external ---------
import pyttsx3
import librosa
from mutagen.mp3 import MP3
from pygame import mixer


ANSI_COLORS = [
    '\033[0;31m',  # red
    '\033[0;32m',  # green
    '\033[1;37m',  # white
]


def read_file(file_path: str, priority: int):
    """ Read config file data

    Args:
        file_path (str): path of the file
        priority (int): priority of the file

    Returns:
        Any: can return a dictionary or list
    """
    # check the file exists or not
    if not os.path.exists(file_path):
        message = f'{ANSI_COLORS[0]} {file_path} not found'
        if priority == 1:
            message += f' can\'t run the program {ANSI_COLORS[2]}'
            quit()
        else:
            message += ANSI_COLORS[2]

        print(message)
        return []

    _, file_extension = os.path.splitext(file_path)

    with open(file_path) as file:
        if file_extension == '.json':
            data = json.load(file)
        else:
            data = list(filter(lambda x: len(x) > 0, file.read().split('\n')))

    return data


def text_to_speech(text: str, enabled: bool):
    """ Text to speech

    Args:
        text (str): text that function speak
        enabled (bool): feature enabled or not by the user
    """
    print(text)
    if enabled:
        engine = pyttsx3.init()
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


def main():
    """ Main function of this project, responsible for playing sounds, reading configration file
        exercise reminders etc.

    """
    global exercise_start

    # ----------- load configrations -----------
    config_data = read_file('../config.json', 1)

    try:
        exercise_reminder_sound_path = config_data['exercise_reminder_sound_path']
        exercise_reminder_volume = config_data['exercise_reminder_volume']
        exercise_beep_sound_path = config_data['exercise_beep_sound_path']
        exercise_tic_sound_path = config_data['exercise_tic_sound_path']
        exercise_text_file_path = config_data['exercise_text_file_path']
        tips_text_file_path = config_data['tips_text_file_path']
        exercise_time = math.ceil(config_data['exercise_time'] / 2)
        exercise_interval_time = config_data['exercise_interval_time']
        break_time = config_data['break_time']
        text_to_speech_enabled = config_data['text_to_speech_enabled']
        tips_enabled = config_data['tips_enabled']
        tic_sound = config_data['tic_sound']
        sections = config_data['sections']

    except KeyError as key:
        print(f'{ANSI_COLORS[0]} Key error for {key} {ANSI_COLORS[1]}')
        quit()

    print(f'{ANSI_COLORS[1]} Configuration loaded successfully... {ANSI_COLORS[2]}')

    current_section = 1
    exercise_list = read_file(exercise_text_file_path, 0)

    if exercise_reminder_sound_path == 'default':
        exercise_reminder_sound_path = '../music/reminder.mp3'

    if exercise_beep_sound_path == 'default':
        exercise_beep_sound_path = '../music/beep.wav'

    if exercise_tic_sound_path == 'default':
        exercise_tic_sound_path = '../music/tic.mp3'

    if tips_enabled:
        tips = read_file(tips_text_file_path, 0)
    else:
        tips = []

    text_to_speech(f"\nEye Exercise Start at {datetime.datetime.now().strftime('%I:%M %p')}\n", text_to_speech_enabled)

    while True:
        time.sleep(exercise_interval_time)
        exercise_start = True

        if exercise_interval_time == 0:
            exercise_interval_time = config_data['exercise_interval_time']

        text_to_speech(f"Exercise {current_section} started", text_to_speech_enabled)

        if len(exercise_list) > 0:
            random_exercise = random.choice(exercise_list)
            text_to_speech(f"You can do: {random_exercise}", text_to_speech_enabled)

        play_sound(exercise_reminder_sound_path, exercise_reminder_volume)

        # start a separate thread to play beep sound
        beep_sound_thread = Thread(target=play_beep_sound,
                                   args=(exercise_reminder_sound_path, exercise_beep_sound_path))
        beep_sound_thread.daemon = True
        beep_sound_thread.start()

        while True:
            if input('Enter S when ready: ').lower() == 's':
                exercise_start = False
                mixer.music.stop()  # stop the reminder music

                text_to_speech(f'Your {exercise_time * 2} seconds eye exercise started.', text_to_speech_enabled)

                # play tic sound if enabled
                if tic_sound:
                    play_sound(exercise_tic_sound_path)

                time.sleep(exercise_time)

                # speak health tip if enabled
                start = time.time()

                if len(tips) > 0:
                    random_tip = random.choice(tips)
                    text_to_speech(random_tip, text_to_speech_enabled)
                else:
                    text_to_speech(f'{exercise_time} seconds passed', text_to_speech_enabled)

                end = exercise_time - (time.time() - start)
                sleep_time = end if end > 0 else 0

                time.sleep(sleep_time)
                mixer.music.stop()  # stop the tic music

                text_to_speech(f"Section {current_section} Done at {datetime.datetime.now().strftime('%I:%M %p')}\n",
                               text_to_speech_enabled)

                break

        if current_section == sections:
            text_to_speech(f'{int(break_time / 60)} minute break time', text_to_speech_enabled)

            counter = 0

            for i in [math.ceil(break_time / 3)] * 3:
                counter += i
                time.sleep(i)
                text_to_speech(f'{counter} seconds passed', text_to_speech_enabled)

            text_to_speech('Break time over\n', text_to_speech_enabled)

            current_section = 0
            exercise_interval_time = 0

        current_section += 1


if __name__ == '__main__':
    main()
    