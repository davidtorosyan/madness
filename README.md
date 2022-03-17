# madness

## Table of contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Usage](#usage)
- [Contribute](#contribute)

## Introduction

This is a tool for predicting March Madness tournament results, which it does in three steps:
* Download the bracket from [ESPN](https://fantasy.espn.com/tournament-challenge-bracket/)
* Download player stats from [CBS](https://www.cbssports.com/college-basketball/teams/)
* Simulate the bracket, predicting winners for each match

To see the results of running this tool, check out the sister-repository [madness-results](https://github.com/davidtorosyan/madness-results).

Note that these predictions are just for fun, and probably no better than random.
## Setup

Install conda (through [anaconda](https://docs.anaconda.com/anaconda/install/) or [miniconda](https://docs.conda.io/en/latest/miniconda.html)), then run:

```sh
conda env update -f conda.yaml --prune
conda activate madness
```

This will install all necessary dependencies.

## Usage

To run the script:
```sh
python src/madness.py
```

Some notes:
* First time running will take a while, since it'll have to download a lot of files
* Downloads and intermediary output is cached, so subsequent runs will be faster
* You can find results under `%AppData%\madness\` on Windows
* This has only been tested *before* a bracket begins

Future work will include:
* Adding command line arguments
* Adding proper logging
* Adding support for predicting brackets that are completed/in progress
* Oh, and improving the prediction algorithm

## Contribute

This project isn't quite ready for pull requests, but please open issues or email me if you're interested.