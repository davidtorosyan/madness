#!/usr/bin/env python

import os.path

from common import DEFAULT_YEAR, data_dir_assert
from bracket import Team, Bracket, get_bracket
from summary import Summary, get_summary_for_team
from stats import get_stats_for_team
from roster import get_roster_for_team
from home import get_team_urls, TeamInfo
from analysis import get_analysis
from tourney import get_tourney_results, pretty_bracket

from typing import List

RESULTS_FILENAME = 'results.txt'

def main():
    print('Running tournament!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    summaries = get_summaries_for_bracket(year, bracket)
    analysis = get_analysis(year, summaries)
    result = get_tourney_results(year, bracket, summaries)
    save_bracket(year, result)
    print('Done!')

def save_bracket(year: int, result: Bracket):
    pretty = pretty_bracket(result)
    path = os.path.join(data_dir_assert(year), RESULTS_FILENAME)
    with open(path, 'w') as file:
        print(pretty, file=file)

def get_summaries_for_bracket(
    year: int,
    bracket: Bracket,
) -> List[Summary]:
    info = get_team_urls(year, bracket.teams.values())
    return [get_summary(year, team, info) for team in bracket.teams.values()]

def get_summary(
    year: int,
    team: Team,
    info: TeamInfo,
) -> Summary:
    stats = get_stats_for_team(year, team, info)
    roster = get_roster_for_team(year, team, info)
    return get_summary_for_team(year, team, roster, stats)

if __name__ == '__main__':
    main()