#!/usr/bin/env python

from bracket import get_bracket
from common import DEFAULT_YEAR
from stats import get_stat_urls, get_stats_for_team

def main():
    print('Hello, world!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    stat_urls = get_stat_urls(year, bracket.teams.values())
    print(get_stats_for_team(year, bracket.teams[0], stat_urls))

if __name__ == '__main__':
    main()