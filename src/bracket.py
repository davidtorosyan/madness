#!/usr/bin/env python

import json
import os.path
import requests

from collections import namedtuple
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from common import data_dir, data_dir_assert

BRACKET_URL_FORMAT = 'https://fantasy.espn.com/tournament-challenge-bracket/{}/en/bracket'
BRACKET_RAW_FILENAME = 'bracket.html'
EXPECTED_NUM_TEAMS = 64

def matches_per_round():
    num_teams = EXPECTED_NUM_TEAMS
    rounds = []
    while num_teams > 1:
        num_teams = int(num_teams / 2)
        rounds.append(num_teams)
    return rounds

EXPECTED_MATCHES_PER_ROUND = matches_per_round()

class Team(BaseModel):
    name: str
    abbrev: str
    seed: int

class Match(BaseModel):
    index: int
    location: str
    teams: List[Team]
    teams_in_round: int
    next_match_index: Optional[int]

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
    index = int(soup['data-index'])
    next_match_index, teams_in_round = compute_next_match_index(index)
    return Match(
        location = soup['data-location'], 
        index = index,
        teams = [parse_team(t) for t in teams],
        teams_in_round = teams_in_round,
        next_match_index = next_match_index,
    )

def parse_team(soup):
    return Team(
        name = soup.find(class_= 'name').text, 
        abbrev = soup.find(class_= 'abbrev').text, 
        seed = soup.find(class_= 'seed').text,
    )

def compute_next_match_index(index):
    round = 0
    num_matches_in_round = EXPECTED_MATCHES_PER_ROUND[round]
    curr = index
    total_matches = num_matches_in_round
    while curr >= num_matches_in_round:
        curr -= num_matches_in_round
        round += 1
        if round >= len(EXPECTED_MATCHES_PER_ROUND) - 1:
            return (None, 1)
        num_matches_in_round = EXPECTED_MATCHES_PER_ROUND[round]
        total_matches += num_matches_in_round
    ratio = curr / num_matches_in_round
    matches_in_next_round = EXPECTED_MATCHES_PER_ROUND[round+1]
    place_in_next_round = ratio * matches_in_next_round
    result = total_matches + place_in_next_round
    teams_in_round = num_matches_in_round * 2
    return (int(result), teams_in_round)

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