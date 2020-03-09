#!/bin/bash

# runs all scripts in the right order
# once complete, you should have two directories with htmls
# and three jsons
# t_team.json and riders.json are needed for the ontology

mkdir -p riders;
mkdir -p teams;

python3 team_scraper.py;
python3 team_reader.py;
python3 rider_scraper.py;
python3 rider_reader.py;
