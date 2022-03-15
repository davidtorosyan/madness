#!/usr/bin/env python

import os.path
import requests

from common import data_dir, data_dir_assert

BRACKET_URL_FORMAT = 'https://fantasy.espn.com/tournament-challenge-bracket/{}/en/bracket'
BRACKET_RAW_FILENAME = 'bracket.html'

def get_raw_bracket_path(year, force = False):
    raw_bracket_path = os.path.join(data_dir(year), BRACKET_RAW_FILENAME)
    if not os.path.isfile(raw_bracket_path) or force:
        download_bracket(year)
    return raw_bracket_path

def download_bracket(year):
    data_dir = data_dir_assert(year)
    result = requests.get(url = bracket_url(year))
    if result.ok:
        path = os.path.join(data_dir, BRACKET_RAW_FILENAME)
        with open(path, 'w') as bracket_file:
            print(result.text, file=bracket_file)
    else:
        raise Exception('Failed to download bracket with status code: {}'.format(result.status_code))
    
def bracket_url(year):
    return BRACKET_URL_FORMAT.format(year)