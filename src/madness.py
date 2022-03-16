#!/usr/bin/env python

from bracket import parse_raw_bracket
from common import DEFAULT_YEAR

def main():
    print('Hello, world!')
    print(parse_raw_bracket(DEFAULT_YEAR))

if __name__ == '__main__':
    main()