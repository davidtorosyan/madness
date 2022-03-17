#!/usr/bin/env python

from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from home import TeamInfo
from pydantic import BaseModel

from bracket import Team
from common import get_transform_typed, get_or_download_path

ROSTER_TEAM_RAW_FORMAT = 'roster/{}.html'
ROSTER_TEAM_FORMAT = 'roster/{}.json'

class Injury(BaseModel):
    area: str

class Player(BaseModel):
    name: str
    injury: Optional[Injury]

class HeaderColumn(BaseModel):
    index: int
    name: str

class PlayerRow(BaseModel):
    player: Player
    values: List[str]

class Table(BaseModel):
    name: str
    header: List[HeaderColumn]
    rows: List[PlayerRow]

class RosterPage(BaseModel):
    name: str
    url: str
    table: Table

def get_roster_for_team(
        year, 
        team: Team, 
        info: TeamInfo,
        force_transform=False, 
        force_fetch=False,
    ) -> Dict[int, str]:
    filename = ROSTER_TEAM_FORMAT.format(team.safe_abbrev)
    url = info.urls[team.index].roster
    return get_transform_typed(
        year=year, 
        filename=filename,
        raw_func=lambda y,force=False: get_roster_raw(y, url, team.safe_abbrev, force),
        transform_func=parse_roster,
        load_func=RosterPage,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def parse_roster(path: str):
    with open(path) as file:
        soup = BeautifulSoup(file, features='html.parser')
    return RosterPage(
        name = soup.find(class_='PageTitle-header').text.strip(),
        url = soup.find(rel='canonical')['href'],
        table = parse_table(soup.find(class_='TableBase')),
    )

def parse_table(soup: BeautifulSoup) -> Table:
    headers = soup.find_all(class_='TableBase-headTh')
    use_headers = headers[0:1] + headers[2:]
    return Table(
        name = soup.find(class_='TableBase-title').text.strip(),
        header = [parse_header(h, idx) for idx, h in enumerate(use_headers)],
        rows = [parse_row(r) for r in soup.find_all(class_='TableBase-bodyTr')],
    )

def parse_header(soup: BeautifulSoup, idx: int) -> HeaderColumn:
    return HeaderColumn(
        index = idx,
        name = soup.text.strip(),
    )

def parse_row(soup: BeautifulSoup) -> PlayerRow:
    values = soup.find_all(class_='TableBase-bodyTd')
    use_values = values[0:1] + values[2:]
    return PlayerRow(
        player = parse_player(soup.find(class_='CellPlayerName--long')),
        values = [v.text.strip() for v in use_values],
    )

def parse_player(soup: BeautifulSoup) -> Player:
    tooltip = soup.find(class_='Tablebase-tooltipInner')
    return Player(
        name = soup.span.a.text.strip(),
        injury = Injury(area=tooltip.text.strip()) if tooltip else None,
    )

def get_roster_raw(year: int, url: str, safe_abbrev: str, force=False) -> str:
    filename = ROSTER_TEAM_RAW_FORMAT.format(safe_abbrev)
    return get_or_download_path(year, url, filename, force)