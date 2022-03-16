#!/usr/bin/env python

import json
import urllib.parse

from typing import Dict, List, Tuple, Optional
from json import JSONDecodeError

from bs4 import BeautifulSoup
from pydantic import BaseModel

from bracket import Team
from common import get_transform_typed, get_or_download_path

STATS_HOME_URL = 'https://www.cbssports.com/college-basketball/teams/'
STATS_HOME_FILENAME = 'stats_home.html'
STATS_URLS_FILENAME = 'stats_urls.json'
STATS_TEAM_RAW_FORMAT = 'teams/{}.html'
STATS_TEAM_FORMAT = 'teams/{}.json'

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

class StatUrls(BaseModel):
    urls: Dict[int, str]

class Player(BaseModel):
    name: str
    position: str

class HeaderColumn(BaseModel):
    index: int
    name: str
    description: str

class PlayerRow(BaseModel):
    player: Player
    values: List[str]

class Table(BaseModel):
    name: str
    header: List[HeaderColumn]
    rows: List[PlayerRow]

class StatsPage(BaseModel):
    name: str
    url: str
    tables: List[Table]

def get_stats_for_team(
        year, 
        team: Team, 
        urls: StatUrls,
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    filename = STATS_TEAM_FORMAT.format(team.abbrev)
    url = urls.urls[team.index]
    return get_transform_typed(
        year=year, 
        filename=filename,
        raw_func=lambda y,force=False: get_stats_raw(y, url, team.abbrev, force),
        transform_func=parse_stats,
        load_func=StatsPage,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_stats(path: str):
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    return StatsPage(
        name = soup.find(class_='PageTitle-header').text.strip(),
        url = soup.find(rel='canonical')['href'],
        tables = [parse_table(t) for t in soup.find_all(class_='TableBase')],
    )

def parse_table(soup: BeautifulSoup) -> Table:
    return Table(
        name = soup.find(class_='TableBase-title').text.strip(),
        header = [parse_header(h, idx) for idx, h in enumerate(soup.find_all(class_='TableBase-headTh--number'))],
        rows = [parse_row(h) for h in soup.select('.TableBase-bodyTr:not(.TableBase-bodyTr--total)')],
    )

def parse_header(soup: BeautifulSoup, idx: int) -> HeaderColumn:
    return HeaderColumn(
        index = idx,
        name = soup.a.text.strip(),
        description = soup.div.text.strip(),
    )

def parse_row(soup: BeautifulSoup) -> PlayerRow:
    return PlayerRow(
        player = parse_player(soup.find(class_='CellPlayerName--long')),
        values = [v.text.strip() for v in soup.find_all(class_='TableBase-bodyTd--number')],
    )

def parse_player(soup: BeautifulSoup) -> Player:
    return Player(
        name = soup.span.a.text.strip(),
        position = soup.span.span.text.strip(),
    )

def get_stats_raw(year: int, url: str, abbrev: str, force=False) -> str:
    filename = STATS_TEAM_RAW_FORMAT.format(abbrev)
    return get_or_download_path(year, url, filename, force)

def get_stat_urls(
        year, 
        teams: List[Team], 
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    return get_transform_typed(
        year=year, 
        filename=STATS_URLS_FILENAME,
        raw_func=get_stats_home_path,
        transform_func=lambda path: parse_stat_urls(path, teams),
        load_func=StatUrls,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_stat_urls(path: str, teams: List[Team]) -> StatUrls:
    urls = parse_urls(path)
    return StatUrls(
        urls = {t.index: find_url(t, urls) for t in teams},
    )

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