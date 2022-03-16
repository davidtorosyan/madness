import os.path
import requests

from pathlib import Path
from typing import Callable, List, Type, TypeVar, TextIO

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

def get_or_download_path(year: int, url: str, filename: str, force=False):
    path = os.path.join(data_dir(year), filename)
    if not os.path.isfile(path) or force:
        download_path(year, url, filename)
    return path

def download_path(year, url, filename):
    data_dir = data_dir_assert(year)
    result = requests.get(url = url)
    if result.ok:
        path = os.path.join(data_dir, filename)
        with open(path, 'w') as file:
            print(result.text, file=file)
    else:
        raise Exception('Failed to download {} with status code: {}'.format(url, result.status_code))

T = TypeVar('T')

def get_transform(
        year: int, 
        filename: str, 
        raw_func: Callable[[int, bool], str],
        transform_func: Callable[[str], T],
        load_func: Callable[[TextIO], T],
        save_func: Callable[[TextIO, T], None],
        load_exceptions: List[Type],
        force_transform=False, 
        force_fetch=False,
    ) -> T:
    path = os.path.join(data_dir(year), filename)
    if os.path.isfile(path) and not force_transform and not force_fetch:
        try:
            with open(path) as file:
                return load_func(file)
        except (FileNotFoundError, PermissionError) as ex:
            pass # TODO log error
        except Exception as ex:
            if type(ex) in load_exceptions:
                pass # TODO log error
            else:
                raise
    raw_path = raw_func(year, force=force_fetch)
    result = transform_func(raw_path)
    with open(path, 'w') as file:
        save_func(file, result)
    return result