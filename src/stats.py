#!/usr/bin/env python

from typing import Dict, List

from bs4 import BeautifulSoup
from home import TeamInfo
from pydantic import BaseModel

from bracket import Team
from common import get_transform_typed, get_or_download_path

STATS_TEAM_RAW_FORMAT = 'stats/{}.html'
STATS_TEAM_FORMAT = 'stats/{}.json'

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
        info: TeamInfo,
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    filename = STATS_TEAM_FORMAT.format(team.abbrev)
    url = info.urls[team.index].stats
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