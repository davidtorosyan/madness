
from tkinter import SEPARATOR
from bracket import Team, Bracket, Match, EXPECTED_MATCHES_PER_ROUND, EXPECTED_NUM_TEAMS
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
        match.winner = winner
        if match.next_match_index:
            next_match = matches[match.next_match_index]
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

def pretty_bracket(bracket: Bracket) -> str:
    rows = EXPECTED_NUM_TEAMS*2
    cols = len(EXPECTED_MATCHES_PER_ROUND)
    grid = [['']*cols for i in range(rows)]
    row = 0
    previous_round = None
    WINNER_MARK = ' (+)'
    SEPARATOR = '-'*24
    for match in bracket.matches.values():
        if previous_round != match.round:
            previous_round = match.round
            row = 0
        buffer = (match.round+1) * match.round
        row += buffer
        grid[row][match.round] = SEPARATOR
        row += 1
        team_0 = bracket.teams[match.teams[0]]
        team_1 = bracket.teams[match.teams[1]]
        grid[row][match.round] = '({}) {}'.format(team_0.seed, team_0.name) + (WINNER_MARK if match.winner == match.teams[0] else '')
        row += 1
        grid[row][match.round] = '({}) {}'.format(team_1.seed, team_1.name) + (WINNER_MARK if match.winner == match.teams[1] else '')
        row += 1
        grid[row][match.round] = SEPARATOR
        row += 1
        row += buffer
    joined_rows = [' '.join(['{:<32}'.format(c) for c in r]).strip() for r in grid]
    result = '\n'.join(r for r in joined_rows if r)
    return result
        