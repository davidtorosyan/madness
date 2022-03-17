#!/usr/bin/env python

from typing import List, Optional, Dict

from bs4 import BeautifulSoup
from pydantic import BaseModel

from common import get_or_download_path, get_transform_typed

BRACKET_URL_FORMAT = 'https://fantasy.espn.com/tournament-challenge-bracket/{}/en/bracket'
BRACKET_RAW_FILENAME = 'bracket.html'
BRACKET_FILENAME = 'bracket.json'
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
    index: int
    name: str
    abbrev: str
    seed: int
    safe_abbrev: str

class Match(BaseModel):
    index: int
    location: str
    teams: List[int]
    teams_in_round: int
    next_match_index: Optional[int]
    winner: Optional[int] = None

class Bracket(BaseModel):
    matches: Dict[int, Match]
    teams: Dict[int, Team]
    winner: Optional[int] = None

def get_bracket(year, force_transform=False, force_fetch=False) -> Bracket:
    return get_transform_typed(
        year=year, 
        filename=BRACKET_FILENAME,
        raw_func=get_raw_bracket_path,
        transform_func=parse_raw_bracket,
        load_func=Bracket,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_raw_bracket(path):
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    wrapper = soup.find(class_ = 'bracketWrapper')
    matchups = wrapper.find_all(class_ = 'matchup')
    all_teams = []
    parsed = [parse_matchup(m, all_teams) for m in matchups]
    return Bracket(
        matches = {m.index: m for m in parsed},
        teams = {t.index: t for t in all_teams},
    )

def parse_matchup(soup, all_teams: List[Team]):
    teams = soup.find_all(class_ = 'actual')
    parsed_teams = [parse_team(t) for t in teams]
    all_teams.extend(parsed_teams)
    index = int(soup['data-index'])
    next_match_index, teams_in_round = compute_next_match_index(index)
    return Match(
        location = soup['data-location'], 
        index = index,
        teams = [t.index for t in parsed_teams],
        teams_in_round = teams_in_round,
        next_match_index = next_match_index,
    )

def parse_team(soup):
    abbrev = soup.find(class_= 'abbrev').text
    return Team(
        index = soup.parent['data-slotindex'],
        name = soup.find(class_= 'name').text, 
        abbrev = abbrev, 
        seed = soup.find(class_= 'seed').text,
        safe_abbrev = abbrev.replace('/', '_')
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

def get_raw_bracket_path(year, force=False):
    return get_or_download_path(year, bracket_url(year), BRACKET_RAW_FILENAME, force)
    
def bracket_url(year):
    return BRACKET_URL_FORMAT.format(year)