#!/usr/bin/env python

from ctypes.wintypes import HENHMETAFILE
from turtle import position
import stats
import roster

from typing import Callable, Dict, List, Optional

from pydantic import BaseModel

from bracket import Team
from common import get_transform_typed

SUMMARY_TEAM_FORMAT = 'summary/{}.json'
PLACEHOLDER_VALUE = '\u2014'
INCHES_IN_FOOT = 12

class PlayerInfo(BaseModel):
    number: int
    position: str
    height: str
    height_inches: int
    weight_pounds: int
    school_class: str
    hometown: Optional[str]

class OverallStats(BaseModel):
    games_played: int
    games_started: int

class ScoringStats(BaseModel):
    minutes_per_game: float
    points_per_game: float
    field_goals_made: int
    field_goals_attempted: int
    field_goal_percentage: Optional[float]
    three_point_field_goals_made: int
    three_point_field_goals_attempted: int
    three_point_field_goal_percentage: Optional[float]
    free_throws_made: int
    free_throws_attempted: int
    free_throw_percentage: Optional[float]

class DefenseStats(BaseModel):
    offensive_rebounds: int
    defensive_rebounds: int
    total_rebounds: int
    rebounds_per_game: float
    total_steals: int
    steals_per_game: float
    total_blocks: int
    blocks_per_game: float

class AssistsStats(BaseModel):
    total_assists: int
    assists_per_game: float
    turnovers: int
    turnovers_per_game: float
    assists_per_turnover: Optional[float]

class PlayerStats(BaseModel):
    overall: OverallStats
    scoring: ScoringStats
    defense: DefenseStats
    assists: AssistsStats

class Injury(BaseModel):
    area: str

class Player(BaseModel):
    name: str
    injury: Optional[Injury]
    info: PlayerInfo
    stats: Optional[PlayerStats]

class Summary(BaseModel):
    team: Team
    players: List[Player]

def get_summary_for_team(
        year: int, 
        team: Team, 
        roster: roster.RosterPage,
        stats: stats.StatsPage,
        force_transform=False, 
        force_fetch=False,
    ) -> Summary:
    filename = SUMMARY_TEAM_FORMAT.format(team.abbrev)
    return get_transform_typed(
        year=year, 
        filename=filename,
        raw_func=lambda y,force=False: None,
        transform_func=lambda s: get_info(team, roster, stats),
        load_func=Summary,
        force_transform=force_transform,
        force_fetch=force_fetch,
    )

def get_info(
        team: Team, 
        roster: roster.RosterPage,
        stats: stats.StatsPage,
    ) -> Summary:
    return Summary(
        team = team,
        players = [get_player(p, roster, stats) for p in roster.table.rows]
    )

def get_player(
        player_row: roster.PlayerRow,
        roster: roster.RosterPage,
        stats: stats.StatsPage,
    ) -> Player:
    return Player(
        name = player_row.player.name,
        info = convert_info(player_row, roster.table.header),
        stats = convert_stats(player_row.player.name, stats),
        injury = convert_injury(player_row.player.injury)
    )

def convert_stats(name: str, stats: stats.StatsPage) -> Optional[PlayerStats]:
    lookup = {t.name:t for t in stats.tables}
    scoring = lookup['Player Stats - Scoring']
    input = next(filter(lambda row: row.player.name == name, scoring.rows), None)
    if input is None:
        return None
    return PlayerStats(
        overall = convert_overall_stats(name, scoring),
        scoring = convert_scoring_stats(name, scoring),
        defense = convert_defense_stats(name, lookup['Player Stats - Defense']),
        assists = convert_assists_stats(name, lookup['Player Stats - Assists/Turnovers']),
    )

def get_lookup_func(name: str, stats: stats.Table) -> Callable[[str], str]: 
    lookup = {h.name:h.index for h in stats.header}
    input = next(filter(lambda row: row.player.name == name, stats.rows))
    def get_value(name: str) -> str:
        return input.values[lookup[name]]
    return get_value

def convert_overall_stats(name: str, stats: stats.Table) -> OverallStats:
    get_value = get_lookup_func(name, stats)
    return OverallStats(
        games_played = get_value('GP'),
        games_started = get_value('GS'),
    )

def convert_scoring_stats(name: str, stats: stats.Table) -> ScoringStats:
    get_value = get_lookup_func(name, stats)
    return ScoringStats(
        minutes_per_game = get_value('MPG'),
        points_per_game = get_value('PPG'),
        field_goals_made = get_value('FGM'),
        field_goals_attempted = get_value('FGA'),
        field_goal_percentage = none_if_placeholder(get_value('FG%')),
        three_point_field_goals_made = get_value('3FGM'),
        three_point_field_goals_attempted = get_value('3FGA'),
        three_point_field_goal_percentage = none_if_placeholder(get_value('3FG%')),
        free_throws_made = get_value('FTM'),
        free_throws_attempted = get_value('FTA'),
        free_throw_percentage = none_if_placeholder(get_value('FT%')),
    )

def convert_defense_stats(name: str, stats: stats.Table) -> DefenseStats:
    get_value = get_lookup_func(name, stats)
    return DefenseStats(
        offensive_rebounds = get_value('OREB'),
        defensive_rebounds = get_value('DREB'),
        total_rebounds = get_value('REB'),
        rebounds_per_game = get_value('RPG'),
        total_steals = get_value('STL'),
        steals_per_game = get_value('SPG'),
        total_blocks = get_value('BLK'),
        blocks_per_game = get_value('BPG'),
    )

def convert_assists_stats(name: str, stats: stats.Table) -> AssistsStats:
    get_value = get_lookup_func(name, stats)
    return AssistsStats(
        total_assists = get_value('AST'),
        assists_per_game = get_value('APG'),
        turnovers = get_value('TO'),
        turnovers_per_game = get_value('TOPG'),
        assists_per_turnover = none_if_placeholder(get_value('A/TO')),
    )

def convert_info(input: roster.PlayerRow, header: List[roster.HeaderColumn]) -> PlayerInfo:
    lookup = {h.name:h.index for h in header}
    def get_value(name: str) -> str:
        return input.values[lookup[name]]
    height = get_value('HT')
    return PlayerInfo(
        number = get_value('NO'),
        position = get_value('POS'),
        height = height,
        height_inches = convert_height_to_inches(height),
        weight_pounds = get_value('WT'),
        school_class = get_value('CLASS'),
        hometown = none_if_placeholder(get_value('Hometown')),
    )

def none_if_placeholder(input: str) -> Optional[str]:
    return None if input == PLACEHOLDER_VALUE else input

def convert_height_to_inches(input: str) -> int:
    height, inches = input.split('-')
    return int(height)*INCHES_IN_FOOT + int(inches)

def convert_injury(input: Optional[roster.Injury]) -> Optional[Injury]:
    return Injury(
        area = input.area.split(':')[0],
    ) if input else None