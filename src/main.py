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


def start_eye_exercise():
    """ Main function of this project, responsible for playing sounds, reading configration file
        exercise reminders etc."""

    # ----------- load configurations -----------
    config_data = read_file('../config.json', 0)

    # ----------- configure values -----------
    exercise_reminder_sound_path: str = catch_key_error("default", config_data, "exercise_reminder_sound_path")
    exercise_beep_sound_path: str = catch_key_error("default", config_data, "exercise_beep_sound_path")
    exercise_tic_sound_path: str = catch_key_error("default", config_data, "exercise_tic_sound_path")
    exercise_text_file_path: str = catch_key_error("text_files/exercise.txt", config_data, "exercise_text_file_path")
    tips_text_file_path: str = catch_key_error("text_files/tips.txt", config_data, "tips_text_file_path")
    exercise_time: int = catch_key_error(60, config_data, "exercise_time") // 2
    exercise_interval_time: int = catch_key_error(600, config_data, "exercise_interval_time")
    break_time: int = catch_key_error(900, config_data, "break_time")
    text_to_speech_enabled: bool = catch_key_error(True, config_data, "text_to_speech_enabled")
    news_scraper_enabled: bool = catch_key_error(True, config_data, "news_scraper_enabled")
    news_scraper_ip: str = catch_key_error(None, config_data, "news_scraper_ip")
    news_category: str = catch_key_error("news", config_data, "news_category")
    tips_enabled: bool = catch_key_error(True, config_data, "tips_enabled")
    tic_sound: bool = catch_key_error(True, config_data, "tic_sound")
    exercise_reminder_volume: float = catch_key_error(0.3, config_data, "exercise_reminder_volume")
    gtts_volume: int = catch_key_error(0, config_data, "gtts_volume")
    sections: int = catch_key_error(5, config_data, "sections")

    print(f'{ANSI_COLORS[1]} Configuration loaded... {ANSI_COLORS[2]}')

    current_section: int = 1
    exercise_list: List = read_file(exercise_text_file_path, 0)
    tips: List = []

    if exercise_reminder_sound_path == 'default':
        exercise_reminder_sound_path = '../music/reminder.mp3'

    if exercise_beep_sound_path == 'default':
        exercise_beep_sound_path = '../music/beep.wav'

    if exercise_tic_sound_path == 'default':
        exercise_tic_sound_path = '../music/tic.mp3'

    if tips_enabled:
        tips = read_file(tips_text_file_path, 0)

    text_to_speech(f"\nEye Exercise Start at {datetime.datetime.now().strftime('%I:%M %p')}\n", text_to_speech_enabled)

    while True:
        time.sleep(exercise_interval_time)
        toggle_exercise_start()

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
                toggle_exercise_start()
                mixer.music.stop()  # stop the reminder music

                text_to_speech(f'Your {exercise_time * 2} seconds eye exercise started.', text_to_speech_enabled)

                # play tic sound if enabled
                if tic_sound:
                    play_sound(exercise_tic_sound_path)

                time.sleep(exercise_time)

                # speak health tip or read news if enabled, higher priority is given to news
                start = time.perf_counter()

                if check_reminders(os.path.join(os.getcwd(), "text_files/reminders.txt"), exercise_interval_time):
                    pass

                elif news_scraper_enabled and news_scraper_ip and news_category:
                    data = get_headline(news_scraper_ip, news_category)
                    if data:
                        google_text_to_speech(f"{data['title']}\n{data['description']}",
                                              text_to_speech_enabled, gtts_volume)
                        print(data["url"])
                    else:
                        text_to_speech(f'{exercise_time} seconds passed', text_to_speech_enabled)

                elif tips_enabled:
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
    start_eye_exercise()
    # print(globals()["get_market_stats"]("13.126.65.194", "nse"))
    # print(check_reminders("../src/text_files/reminders.txt"))
