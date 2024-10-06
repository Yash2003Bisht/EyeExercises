# --------- built-in ---------
import sys
import random
import time
import select  # not available on windows

# --------- external ---------
import librosa
from mutagen.mp3 import MP3

# --------- internal ---------
from eye_exercise.helper import *
# all need to be imported from reminders because we need to run reminder function from here
from eye_exercise.reminders import *


def handle_half_time_tasks():
    """ Handle the tasks to be executed after exercise_time/2 seconds """
    # create a time counter to keep the track of execution time
    start = time.perf_counter()

    # check reminders
    details = check_reminders(os.path.join(os.getcwd(), "text_files/reminders.txt"),
                              int(os.environ["exercise_interval_time"]))
    # load frequent use variables
    text_to_speech_enabled, exercise_time = (is_true(os.environ.get("text_to_speech_enabled", "true")),
                                             int(os.environ["exercise_time"]) // 2)

    # func_to_exec - stores the function address that we will run after half of exercise_time is left
    # args - stores arguments of the function

    if details:
        func_to_exec = [detail["func"] for detail in details]
        args = [detail["args"] for detail in details]

    elif (is_true(os.environ.get("news_scraper_enabled", "false")) and os.environ.get("news_scraper_ip", "")
          and os.environ.get("news_category", "")):
        data = get_headline(os.environ["news_scraper_ip"], os.environ["news_category"], exercise_time)
        if data:
            gtss_text_to_speech_enabled = is_true(os.environ.get("gtss_text_to_speech_enabled", "false"))
            func_to_exec = [google_text_to_speech]
            args = [(f"{data['title']}\n{data['description']}",
                     gtss_text_to_speech_enabled, int(os.environ["gtts_volume"]), "hi", data["url"])]
        else:
            func_to_exec = [text_to_speech]
            args = [(f'{exercise_time} seconds passed', text_to_speech_enabled)]

    elif is_true(os.environ.get("tips_enabled", "true")):
        random_tip = random.choice(read_file(os.environ["tips_text_file_path"], 0))
        func_to_exec = [text_to_speech]
        args = [(random_tip, text_to_speech_enabled)]

    else:
        func_to_exec = [text_to_speech]
        args = [(f'{exercise_time} seconds passed', text_to_speech_enabled)]

    # calculate the remaining time
    execution_time = time.perf_counter() - start
    delay = max(0, int(exercise_time - execution_time))

    # sleep for "delay" seconds
    time.sleep(delay)

    # start executing functions
    for func, arguments in zip(func_to_exec, args):
        func(*arguments)


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

    # don't run the beep sound if the exercise is in pause state
    if exercise_paused:
        return None

    # "exercise_start" variable is in helper.py
    # import it from there
    from eye_exercise.helper import exercise_start

    while exercise_start:
        # play beep sound after every 60 seconds
        time.sleep(60)

        # import the "exercise_start" from helper.py in each iteration
        # since the state of it will change there
        from eye_exercise.helper import exercise_start

        if exercise_start:
            play_sound(beep_sound_path)
            continue

        # break the loop if exercise is already ended
        break


def continue_execution(timeout: int):
    """
    Takes the input from user to continue the execution
    """
    # set a timeout for input
    timeout = timeout
    start_time = time.time()

    while True:
        # check if input is available
        if select.select([sys.stdin], [], [], timeout - (time.time() - start_time))[0]:
            user_input = input().lower()
            if user_input == 'c':
                toggle_exercise_paused()
                break
        else:
            break
