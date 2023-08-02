"""
@author: Yash Bisht
@date: 02/10/2022
@description: Eye Exercise Reminder
"""
# --------- built-in ---------
import random
import math
from threading import Thread

# --------- internal ---------
from eye_exercise.tasks import *
from eye_exercise.reminders import *
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
    exercise_time = int(os.environ["exercise_time"]) // 2
    exercise_interval_time = int(os.environ["exercise_interval_time"])
    break_time = int(os.environ["break_time"])
    exercise_reminder_volume = float(os.environ["exercise_reminder_volume"])
    text_to_speech_enabled = is_true(os.environ.get("text_to_speech_enabled", "true"))

    print(f'{ANSI_COLORS[1]} Configuration loaded... {ANSI_COLORS[2]}')

    current_section: int = 1
    exercise_list: List = read_file(os.environ["exercise_text_file_path"], 0)
    tips: List = []

    if is_true(os.environ.get("tips_enabled", "true")):
        tips = read_file(os.environ["tips_text_file_path"], 0)

    text_to_speech(f"\nEye Exercise Start at {datetime.datetime.now().strftime('%I:%M %p')}\n", text_to_speech_enabled)

    while True:
        time.sleep(exercise_interval_time)
        toggle_exercise_start()

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
            if input('Enter S when ready: ').lower() == 's':
                toggle_exercise_start()
                mixer.music.stop()  # stop the reminder music

                text_to_speech(f'Your {exercise_time * 2} seconds eye exercise started.', text_to_speech_enabled)

                # play tic sound if enabled
                if is_true(os.environ.get("tic_sound", "true")):
                    play_sound(os.environ["exercise_tic_sound_path"])

                time.sleep(exercise_time)

                # speak health tip or read news if enabled, higher priority is given to news
                start = time.perf_counter()

                if check_reminders(os.path.join(os.getcwd(), "text_files/reminders.txt"), exercise_interval_time):
                    pass

                elif news_scraper_enabled and news_scraper_ip and news_category:
                    data = get_headline(news_scraper_ip, news_category)
                    if data:
                        google_text_to_speech(f"{data['title']}\n{data['description']}",
                                              text_to_speech_enabled, int(os.environ["gtts_volume"]))
                        print(data["url"])
                    else:
                        text_to_speech(f'{exercise_time} seconds passed', text_to_speech_enabled)

                elif is_true(os.environ.get("tips_enabled", "true")):
                    random_tip = random.choice(tips)
                    text_to_speech(random_tip, text_to_speech_enabled)

                else:
                    text_to_speech(f'{exercise_time} seconds passed', text_to_speech_enabled)

                end = exercise_time - int(time.perf_counter() - start)
                sleep_time = max(0, end)

                time.sleep(sleep_time)
                mixer.music.stop()  # stop the tic music

                text_to_speech(f"Section {current_section} Done at {datetime.datetime.now().strftime('%I:%M %p')}\n",
                               text_to_speech_enabled)

                break

        if current_section == int(os.environ["sections"]):
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
    start_eye_exercise()
    # print(globals()["get_market_stats"]("13.126.65.194", "nse"))
    # print(check_reminders("../src/text_files/reminders.txt"))
