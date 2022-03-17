#!/usr/bin/env python

from bracket import get_bracket
from common import DEFAULT_YEAR
from home import get_team_urls
from stats import get_stats_for_team
from roster import get_roster_for_team
from summary import get_summary_for_team

def main():
    print('Hello, world!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    stat_urls = get_team_urls(year, bracket.teams.values())
    stats = get_stats_for_team(year, bracket.teams[0], stat_urls)
    roster = get_roster_for_team(year, bracket.teams[0], stat_urls)
    print(get_summary_for_team(year, bracket.teams[0], roster, stats, force_transform=True))

if __name__ == '__main__':
    main()