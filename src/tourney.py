
from bracket import Team, Bracket, Match
from summary import Summary
from common import get_transform_typed

from typing import Dict, List

TOURNEY_FILENAME = 'tourney.json'

def get_tourney_results(
        year: int, 
        bracket: Bracket, 
        summaries: List[Summary],
        force_transform=False, 
    ) -> Bracket:
    return get_transform_typed(
        year=year, 
        filename=TOURNEY_FILENAME,
        raw_func=lambda y,force=False: None,
        transform_func=lambda s: run_tourney(bracket, summaries),
        load_func=Bracket,
        force_transform=force_transform,
    )

def run_tourney(bracket: Bracket, summaries: List[Summary]) -> Bracket:
    matches = bracket.matches.copy()
    teams = {s.team.index:s for s in summaries}
    overall_winner = None
    for match in matches.values():
        winner = play_match(match, teams)
        if match.next_match_index:
            next_match = matches[match.next_match_index]
            match.winner = winner
            next_match.teams.append(winner)
        else:
            overall_winner = winner
    return Bracket(
        matches = matches,
        teams = bracket.teams,
        winner = overall_winner,
    )

def play_match(match: Match, teams: Dict[int, Summary]):
    return match.teams[0]