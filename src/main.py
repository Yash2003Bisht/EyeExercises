"""
@author: Yash Bisht
@date: 02/10/2022
@description: Eye Exercise Reminder
"""
# --------- built-in ---------
import math
from threading import Thread
from multiprocessing import Process

# --------- internal ---------
from eye_exercise.tasks import *
from eye_exercise.helper import *

# ----------- load configurations -----------
load_env()


def start_eye_exercise():
    """ Main function of this project, responsible for playing sounds, reading configration file
        exercise reminders, etc."""

    # ---------------------- pre-checks ----------------------
    if os.environ.get("exercise_reminder_sound_path", "default") == "default":
        os.environ["exercise_reminder_sound_path"] = '../music/reminder.mp3'

    if os.environ.get("exercise_beep_sound_path", "default") == "default":
        os.environ["exercise_beep_sound_path"] = '../music/beep.wav'

    if os.environ.get("exercise_tic_sound_path", "default") == "default":
        os.environ["exercise_tic_sound_path"] = '../music/tic.mp3'

    if os.environ.get("exercise_text_file_path", "default") == "default":
        os.environ["exercise_text_file_path"] = "text_files/exercise.txt"

    if os.environ.get("tips_text_file_path", "default") == "default":
        os.environ["tips_text_file_path"] = "text_files/tips.txt"

    # ---------------------- load frequent use variables ----------------------
    exercise_time = int(os.environ["exercise_time"])
    exercise_interval_time = int(os.environ["exercise_interval_time"])
    break_time = int(os.environ["break_time"])
    exercise_reminder_volume = float(os.environ["exercise_reminder_volume"])
    text_to_speech_enabled = is_true(os.environ.get("text_to_speech_enabled", "true"))
    exercise_list: List = read_file(os.environ["exercise_text_file_path"], 0)
    current_section: int = 1

    print(f'{ANSI_COLORS[1]}Configuration loaded... {ANSI_COLORS[2]}')

    # check news logs
    if os.path.exists("logs/news_logs.log"):
        print(f"{ANSI_COLORS[0]}News logs found!  {ANSI_COLORS[2]}")

    text_to_speech(f"\nEye Exercise Start at {datetime.datetime.now().strftime('%I:%M %p')}\n",
                   text_to_speech_enabled)

    while True:
        time.sleep(exercise_interval_time)
        toggle_exercise_start(to=True)

        if exercise_interval_time == 0:
            exercise_interval_time = int(os.environ["exercise_interval_time"])

        text_to_speech(f"Exercise {current_section} started", text_to_speech_enabled)

        if len(exercise_list) > 0:
            random_exercise = random.choice(exercise_list)
            text_to_speech(f"You can do: {random_exercise}", text_to_speech_enabled)

        play_sound(os.environ["exercise_reminder_sound_path"], exercise_reminder_volume)

        # start a separate thread to play beep sound
        beep_sound_thread = Thread(target=play_beep_sound,
                                   args=(os.environ["exercise_reminder_sound_path"],
                                         os.environ["exercise_beep_sound_path"]))
        beep_sound_thread.daemon = True
        beep_sound_thread.start()

        while True:
            user_input = input('Enter S when ready: ').lower()

            if user_input == 's':
                toggle_exercise_start(to=False)
                mixer.music.stop()  # stop the reminder music

                text_to_speech(f'Your {exercise_time} seconds eye exercise started.', text_to_speech_enabled)

                # play tic sound if enabled
                if is_true(os.environ.get("tic_sound", "true")):
                    play_sound(os.environ["exercise_tic_sound_path"])

                # create a separate process to handle background tasks
                Process(target=handle_half_time_tasks).start()

                # sleep the program for "exercise_time" seconds
                # so that above-created thread can be started
                # because of python's GIL we can't run more than 1 thread simultaneously
                # GIL will only allow multithreading for IO/CPU bounds tasks
                time.sleep(exercise_time)

                # stop the tic music once "exercise_time" is finished
                mixer.music.stop()

                text_to_speech(f"Section {current_section} Done at {datetime.datetime.now().strftime('%I:%M %p')}\n",
                               text_to_speech_enabled)

                break

            elif user_input.startswith('p'):
                # pause the execution for 'n*60' seconds
                try:
                    n = int(user_input.split("-")[1])
                except (ValueError, IndexError, TypeError):
                    continue

                print(f"Pausing execution for {n} minutes. Enter 'c' to continue.")

                # toggle exercise paused and start
                toggle_exercise_paused(to=True)
                toggle_exercise_start(to=False)

                # stop the reminder music
                mixer.music.stop()

                # stop the execution for n*60 seconds
                total_seconds = n*60

                # create a thread to take the user to continue the execution
                Thread(target=continue_execution, args=(total_seconds,)).start()

                while total_seconds:
                    if not toggle_exercise_paused(required_value=True):
                        break
                    time.sleep(1)
                    total_seconds -= 1

                # toggle exercise paused and start
                if toggle_exercise_paused(required_value=True):
                    toggle_exercise_paused(to=False)
                    toggle_exercise_start(to=True)

                # play the reminder sound
                play_sound(os.environ["exercise_reminder_sound_path"], exercise_reminder_volume)

                # start a separate thread to play beep sound
                beep_sound_thread = Thread(target=play_beep_sound,
                                           args=(os.environ["exercise_reminder_sound_path"],
                                                 os.environ["exercise_beep_sound_path"]))
                beep_sound_thread.daemon = True
                beep_sound_thread.start()

        # --------------------------------- break time ---------------------------------
        if current_section == int(os.environ["sections"]):
            text_to_speech(f'{int(break_time / 60)} minute break time', text_to_speech_enabled)

            counter = 0

            # divide break time into 3 equal parts and sleep on each iteration
            for i in [math.ceil(break_time / 3)] * 3:
                counter += i
                time.sleep(i)
                text_to_speech(f'{counter} seconds passed', text_to_speech_enabled)

            text_to_speech('Break time over\n', text_to_speech_enabled)

            # reload the section
            current_section = 0
            exercise_interval_time = 0

        current_section += 1


if __name__ == '__main__':
    try:
        start_eye_exercise()

    except KeyboardInterrupt:
        print("quitting")

        # delete new logs if exists
        news_log_path = "logs/news_logs.log"
        if os.path.exists(news_log_path):
            os.system(f"rm -rf {news_log_path}")

    finally:
        # delete the program_state json file
        if os.path.exists("text_files/.program_state.json"):
            os.remove("text_files/.program_state.json")
