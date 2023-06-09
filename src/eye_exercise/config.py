from typing import Dict

from eye_exercise.helper import read_file, catch_key_error


def load_config(config_path: str):
    """ Load the configuration

    Args:
        config_path (str): config file path
    """
    # ----------- load configurations -----------
    config_data: Dict = read_file(config_path, 1)
    config: Dict = {}

    # ----------- configure values -----------
    config.update({
        "exercise_reminder_sound_path": config_data.get("exercise_reminder_sound_path", "default"),
        "exercise_beep_sound_path": config_data.get("exercise_beep_sound_path", "default"),
        "exercise_tic_sound_path": config_data.get("exercise_tic_sound_path", "default"),
        "exercise_text_file_path": config_data.get("exercise_text_file_path", "text_files/exercise.txt"),
        "tips_text_file_path": config_data.get("tips_text_file_path", "text_files/tips.txt"),
        "exercise_time": config_data.get("exercise_time", 60),
        "exercise_interval_time": config_data.get("exercise_interval_time", 600),
        "break_time": config_data.get("break_time", 900),
        "text_to_speech_enabled": config_data.get("text_to_speech_enabled", True),
        "news_scraper_enabled": config_data.get("news_scraper_enabled", True),
        "news_scraper_ip": config_data.get("news_scraper_ip", None),
        "news_category": config_data.get("news_category", "news"),
        "tips_enabled": config_data.get("tips_enabled", True),
        "tic_sound": config_data.get("tic_sound", True),
        "exercise_reminder_volume": config_data.get("exercise_reminder_volume", 0.3),
        "gtts_volume": config_data.get("gtts_volume", 0),
        "sections": config_data.get("sections", 5),
    })

    return config
