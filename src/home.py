#!/usr/bin/env python

import json
import urllib.parse

from typing import Dict, List, Tuple

from bs4 import BeautifulSoup
from pydantic import BaseModel

from bracket import Team
from common import get_transform_typed, get_or_download_path

STATS_HOME_URL = 'https://www.cbssports.com/college-basketball/teams/'
STATS_HOME_FILENAME = 'stats_home.html'
STATS_URLS_FILENAME = 'stats_urls.json'

NAME_OVERRIDES = {
    'UConn': 'Connecticut Huskies',
    'CSU Fullerton': 'Cal State Fullerton Titans',
    'Saint Peter\'s': 'St. Peter\'s Peacocks',
    'S Dakota St': 'South Dakota State Jackrabbits',
    'USC': 'Southern California Trojans',
    'J\'Ville St': 'Jacksonville State Gamecocks',
}

class InfoUrls(BaseModel):
    stats: str
    roster: str

class TeamInfo(BaseModel):
    urls: Dict[int, InfoUrls]

def get_team_urls(
        year, 
        teams: List[Team], 
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    return get_transform_typed(
        year=year, 
        filename=STATS_URLS_FILENAME,
        raw_func=get_stats_home_path,
        transform_func=lambda path: parse_team_urls(path, teams),
        load_func=TeamInfo,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_team_urls(path: str, teams: List[Team]) -> TeamInfo:
    urls = parse_urls(path)
    return TeamInfo(
        urls = {t.index: find_url(t, urls) for t in teams},
    )

def find_url(team: Team, urls: List[Tuple[str, str]]) -> InfoUrls:
    override = NAME_OVERRIDES.get(team.name, None)
    team_name = override if override else team.name
    for name, info in urls:
        if team_name in name:
            return info
    raise Exception('Failed to find stats for team: {}'.format(team))

def parse_urls(path: str) -> List[Tuple[str, InfoUrls]]:
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    team_names = soup.find_all(class_='TeamName')
    results = []
    for team_name in team_names:
        name = team_name.a.text
        urls = InfoUrls(
            stats = urllib.parse.urljoin(STATS_HOME_URL, team_name.a['href'] + 'stats/'),
            roster = urllib.parse.urljoin(STATS_HOME_URL, team_name.a['href'] + 'roster/'),
        )
        results.append((name, urls))
    return results

def get_stats_home_path(year: int, force=False) -> str:
    return get_or_download_path(year, STATS_HOME_URL, STATS_HOME_FILENAME, force)