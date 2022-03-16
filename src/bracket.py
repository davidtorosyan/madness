#!/usr/bin/env python

import json
import os.path
import requests

from collections import namedtuple
from typing import List

from bs4 import BeautifulSoup
from pydantic import BaseModel

from common import data_dir, data_dir_assert

BRACKET_URL_FORMAT = 'https://fantasy.espn.com/tournament-challenge-bracket/{}/en/bracket'
BRACKET_RAW_FILENAME = 'bracket.html'

class Team(BaseModel):
    name: str
    abbrev: str
    seed: int

class Match(BaseModel):
    location: str
    index: int
    teams: List[Team]

def parse_raw_bracket(year):
    path = get_raw_bracket_path(year)
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    wrapper = soup.find(class_ = 'bracketWrapper')
    matchups = wrapper.find_all(class_ = 'matchup')
    parsed = [parse_matchup(m) for m in matchups]
    return parsed

def parse_matchup(soup):
    teams = soup.find_all(class_ = 'actual')
    return Match(
        location = soup['data-location'], 
        index = soup['data-index'],
        teams = [parse_team(t) for t in teams]
    )

def parse_team(soup):
    return Team(
        name = soup.find(class_= 'name').text, 
        abbrev = soup.find(class_= 'abbrev').text, 
        seed = soup.find(class_= 'seed').text,
    )

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