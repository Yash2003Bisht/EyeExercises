# --------- built-in ---------
import random

# --------- internal ---------
from eye_exercise.helper import *
# all need to be imported from reminders because we need to run reminder function from here
from eye_exercise.reminders import *


def handle_half_time_tasks():
    """ Handle the tasks to be executed after exercise_time/2 seconds """
    # check reminders
    flag, details = check_reminders(os.path.join(os.getcwd(), "text_files/reminders.txt"),
                                    int(os.environ["exercise_interval_time"]))

    # load frequent use variables
    text_to_speech_enabled, exercise_time = (is_true(os.environ.get("text_to_speech_enabled", "true")),
                                             int(os.environ["exercise_time"]) // 2)

    # func_to_exec - stores the function pointer that we will run after half of exercise_time is left
    # args - stores arguments of the function

    if flag:
        func_to_exec = details["func"]
        args = details["args"]

    elif (is_true(os.environ.get("news_scraper_enabled", "false")) and os.environ.get("news_scraper_ip", "")
          and os.environ.get("news_category", "")):
        data = get_headline(os.environ["news_scraper_ip"], os.environ["news_category"])
        if data:
            func_to_exec = google_text_to_speech
            args = (f"{data['title']}\n{data['description']}",
                    text_to_speech_enabled, int(os.environ["gtts_volume"]), "hi", data["url"])
        else:
            func_to_exec = text_to_speech
            args = (f'{exercise_time} seconds passed', text_to_speech_enabled)

    elif is_true(os.environ.get("tips_enabled", "true")):
        random_tip = random.choice(read_file(os.environ["tips_text_file_path"], 0))
        func_to_exec = text_to_speech
        args = (random_tip, text_to_speech_enabled)

    else:
        func_to_exec = text_to_speech
        args = (f'{exercise_time} seconds passed', text_to_speech_enabled)

    # sleep for half the time
    time.sleep(exercise_time)

    # execute function
    func_to_exec(*args)
