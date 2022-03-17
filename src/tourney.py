
from tkinter import SEPARATOR
from bracket import Team, Bracket, Match, EXPECTED_MATCHES_PER_ROUND, EXPECTED_NUM_TEAMS
from summary import Summary
from common import get_transform_typed
from analysis import Score, TeamScore, score_teams

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
    final_score = None
    for match in matches.values():
        winner = play_match(match, teams)
        match.winner = winner
        if match.next_match_index:
            next_match = matches[match.next_match_index]
            next_match.teams.append(winner)
        else:
            overall_winner = winner
            final_score = get_final_score(match, teams)
    return Bracket(
        matches = matches,
        teams = bracket.teams,
        winner = overall_winner,
        final_score = final_score,
    )

def get_final_score(match: Match, teams: Dict[int, Summary]) -> List[int]:
    return [get_score(teams[t]) for t in match.teams]

def get_score(summary: Summary):
    return sum([p.stats.scoring.points_per_game for p in summary.players if p.stats])

def play_match(match: Match, teams: Dict[int, Summary]):
    analysis = score_teams([teams[t] for t in match.teams], match.location)
    return choose_winner(analysis.teams[0], analysis.teams[1]).index

def choose_winner(left: TeamScore, right: TeamScore) -> TeamScore:
    counter = 0
    counter += 1 if left.score.strength > right.score.strength else -1
    counter += 1 if left.score.dexterity > right.score.dexterity else -1
    counter += 1 if left.score.constitution > right.score.constitution else -1
    counter += 1 if left.score.intelligence > right.score.intelligence else -1
    counter += 1 if left.score.wisdom > right.score.wisdom else -1
    counter += 1 if left.score.charisma > right.score.charisma else -1
    if counter > 0:
        return left
    elif counter < 0:
        return right
    elif left.score.power >= right.score.power:
        return left
    else:
        return right

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
        