#!/usr/bin/env python

import json
import urllib.parse

from typing import Dict, List, Tuple, Optional
from json import JSONDecodeError

from bs4 import BeautifulSoup

from bracket import Team
from common import get_transform, get_or_download_path

STATS_HOME_URL = 'https://www.cbssports.com/college-basketball/teams/'
STATS_HOME_FILENAME = 'stats_home.html'
STATS_URLS_FILENAME = 'stats_urls.json'

NAME_OVERRIDES = {
    'UConn': 'Connecticut Huskies',
    'RUTG/ND': 'Rutgers Scarlet Knights',
    'CSU Fullerton': 'Cal State Fullerton Titans',
    'WYO/IU': 'Wyoming Cowboys',
    'Saint Peter\'s': 'St. Peter\'s Peacocks',
    'WRST/BRY': 'Bryant Bulldogs',
    'TXSO/TCC': 'Texas Southern Tigers',
    'S Dakota St': 'South Dakota State Jackrabbits',
    'USC': 'Southern California Trojans',
    'J\'Ville St': 'Jacksonville State Gamecocks',
}

def get_stat_urls(
        year, 
        teams: List[Team], 
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    return get_transform(
        year=year, 
        filename=STATS_URLS_FILENAME,
        raw_func=get_stats_home_path,
        transform_func=lambda path: parse_stat_urls(path, teams),
        load_func=lambda fp: json.load(fp),
        save_func=lambda fp, result: json.dump(result, fp, indent=2),
        load_exceptions=[JSONDecodeError],
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_stat_urls(path: str, teams: List[Team]) -> Dict[int, str]:
    urls = parse_urls(path)
    return {t.index: find_url(t, urls) for t in teams}

def find_url(team: Team, urls: List[Tuple[str, str]]) -> str:
    override = NAME_OVERRIDES.get(team.name, None)
    team_name = override if override else team.name
    for name, url in urls:
        if team_name in name:
            return url
    raise Exception('Failed to find stats for team: {}'.format(team))

def parse_urls(path: str) -> List[Tuple[str, str]]:
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    team_names = soup.find_all(class_='TeamName')
    results = []
    for team_name in team_names:
        name = team_name.a.text
        relative_url = team_name.a['href'] + 'stats/'
        url = urllib.parse.urljoin(STATS_HOME_URL, relative_url) 
        results.append((name, url))
    return results

def get_stats_home_path(year: int, force=False) -> str:
    return get_or_download_path(year, STATS_HOME_URL, STATS_HOME_FILENAME, force)