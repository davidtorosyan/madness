#!/usr/bin/env python

from common import DEFAULT_YEAR
from bracket import Team, Bracket, get_bracket
from summary import Summary, get_summary_for_team
from stats import get_stats_for_team
from roster import get_roster_for_team
from home import get_team_urls, TeamInfo
from analysis import get_analysis
from tourney import get_tourney_results

from typing import List

def main():
    print('Hello, world!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    summaries = get_summaries_for_bracket(year, bracket)
    # print(get_analysis(year, summaries, force_transform=True))
    print(get_tourney_results(year, bracket, summaries, force_transform=True))

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