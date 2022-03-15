import os.path

from pathlib import Path

from appdirs import AppDirs

APP_NAME = 'madness'
APP_AUTHOR = 'davidtorosyan'

dirs = AppDirs(APP_NAME, APP_AUTHOR)
DATA_DIR = dirs.user_data_dir

DEFAULT_YEAR = 2022

def data_dir(year):
    return os.path.join(DATA_DIR, str(year))

def data_dir_assert(year):
    path = data_dir(year)
    Path(path).mkdir(parents=True, exist_ok=True)
    return path
