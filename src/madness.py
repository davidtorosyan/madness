#!/usr/bin/env python

from bracket import get_bracket
from common import DEFAULT_YEAR
from stats import stat_urls

def main():
    print('Hello, world!')
    year = DEFAULT_YEAR
    bracket = get_bracket(year)
    print(stat_urls(year, bracket.teams.values()))

if __name__ == '__main__':
    main()