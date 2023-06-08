from helper import read_file, catch_key_error


def load_config(config_path: str):
    """ Load the configuration

    Args:
        config_path (str): config file path
    """
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

