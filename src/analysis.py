
from statistics import mean
from summary import Summary, Player
from common import get_transform_typed

from typing import Callable, List, Tuple

from pydantic import BaseModel

ANALYSIS_FILENAME = 'analysis.json'
DEFAULT_HEIGHT_INCHES = 72
DEFAULT_WEIGHT_POUNDS = 200
DEFAULT_PERCENTAGE = 20
MINUTES_IN_GAME = 40

class Score(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

class PlayerScore(BaseModel):
    name: str
    score: Score
    minutes: int

class TeamScore(BaseModel):
    name: str
    seed: int
    score: Score
    players: List[PlayerScore]

class Analysis(BaseModel):
    teams: List[TeamScore]

def get_analysis(
        year: int, 
        teams: List[Summary], 
        force_transform=False, 
    ) -> Analysis:
    return get_transform_typed(
        year=year, 
        filename=ANALYSIS_FILENAME,
        raw_func=lambda y,force=False: None,
        transform_func=lambda s: score_teams(teams),
        load_func=Summary,
        force_transform=force_transform,
    )

def score_teams(teams: List[Summary]) -> Analysis:
    return Analysis(
        teams = [score_team(s) for s in teams]
    )

def score_team(team: Summary) -> TeamScore:
    players = [p for p in team.players if p.stats]
    player_scores = [score_player(p) for p in players]
    return TeamScore(
        name = team.team.name,
        seed = team.team.seed,
        score = combine_scores(player_scores),
        players = player_scores,
    )

def combine_scores(players: List[PlayerScore]) -> Score:
    def combine_stat(get_stat: Callable[[PlayerScore], int]) -> int:
        return int(mean([get_stat(p) * p.minutes for p in players]) / MINUTES_IN_GAME)
    return Score(
        strength = combine_stat(lambda p: p.score.strength),
        dexterity = combine_stat(lambda p: p.score.dexterity),
        constitution = combine_stat(lambda p: p.score.constitution),
        intelligence = combine_stat(lambda p: p.score.intelligence),
        wisdom = combine_stat(lambda p: p.score.wisdom),
        charisma = combine_stat(lambda p: p.score.charisma),
    )

def score_player(player: Player) -> PlayerScore:
    return PlayerScore(
        name = player.name,
        score = Score(
            strength = int(
                player.stats.scoring.points_per_game * 
                (player.info.height_inches or DEFAULT_HEIGHT_INCHES)
            ),
            dexterity = int(
                player.stats.defense.steals_per_game *
                (player.stats.scoring.field_goal_percentage or DEFAULT_PERCENTAGE) *
                (player.stats.scoring.three_point_field_goal_percentage or DEFAULT_PERCENTAGE)
            ),
            constitution = int(
                player.stats.defense.blocks_per_game * 
                (player.info.weight_pounds or DEFAULT_WEIGHT_POUNDS)
            ),
            intelligence = int(
                score_intelligence(player.info.school_class)
            ),
            wisdom = int(
                player.stats.defense.rebounds_per_game *
                player.stats.assists.turnovers_per_game * 
                (player.info.height_inches or DEFAULT_HEIGHT_INCHES)
            ),
            charisma = int(
                (player.stats.scoring.free_throw_percentage or DEFAULT_PERCENTAGE) *
                player.stats.assists.assists_per_game
            ),
        ),
        minutes = player.stats.overall.minutes_per_game,
    )

def score_intelligence(school_class: str):
    scores = {
        'Fr': 50,
        'Soph': 100,
        'Jr': 200,
        'Sr': 250,
    }
    return scores.get(school_class, '99')