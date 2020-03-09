# Bertelt Braaksma - s2568217
# extracts relevant information for all teams in teams.json
# outputs json with dict[team_name] and another dict as value

from bs4 import BeautifulSoup
import os
import requests
import simplejson as json
import unidecode

with open("teams.json", "r") as f:
    teams = json.load(f)
    t_teams = dict()
    for team in teams:
        fname = teams[team].split("/")[4] + ".html"
        with open(os.path.join("teams/",fname), "r") as file:
            t_teams[team] = dict()
            page = file.read()
            soup = BeautifulSoup(page, "lxml")
            status, abbreviation, bike = None, None, None
            bs = [b for b in soup.findAll("b")]
            for b in bs:
                if b.string.strip() == "Team status:":
                    try:
                        status = b.next_sibling.strip()
                    except TypeError:
                        print(team)
                if b.string.strip() == "Abbreviation:":
                    abbreviation = b.next_sibling.strip()
                if b.string.strip() == "Bike:":
                    bike = b.next_sibling.strip()

            t_teams[team]["url"] = teams[team]
            t_teams[team]["dbo:status"] = status
            t_teams[team]["dbo:uciCode"] = abbreviation
            t_teams[team]["dbp:bicycles"] = bike

with open("t_teams.json", "w") as outfile:
    json.dump(t_teams, outfile)
