#!/usr/bin/env python

from bracket import get_bracket
from common import DEFAULT_YEAR
from stats import get_stat_urls, get_stats, parse_stats

def main():
    print('Hello, world!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    stat_urls = get_stat_urls(year, bracket.teams.values())
    stats_path = get_stats(year, stat_urls.urls[0], bracket.teams[0].abbrev)
    print(parse_stats(stats_path))

if __name__ == '__main__':
    main()