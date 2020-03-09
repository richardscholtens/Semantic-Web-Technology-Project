# Bertelt Braaksma - s2568217
# downloads all team pages from procyclingstats
# files stored in /teams directory

import datetime as dt
import numpy as np
import os
import requests
import simplejson as json
import time
from bs4 import BeautifulSoup

user_agent = {"User-agent": "Mozilla/5.0"}
teams = dict()

def get_team_urls():
    base_url = "https://www.procyclingstats.com/"
    url = ["teams/worldtour", "teams/continental"]
    for u in url:
        print(base_url + u)
        response = requests.get(base_url + u, headers=user_agent)
        if response.status_code == 200:
            page = response.content
            soup = BeautifulSoup(page, "lxml")
            a = soup.find_all("a")
            pob = None
            for i in a:
                if "team/" in str(i):
                    j = str(i).split('"')
                    if u == "teams/worldtour":
                        if len(j) == 3:
                            name = j[2].split("<")[0].replace(">", "").strip()
                            teams[name] = base_url + j[1]
                    else:
                        if (base_url + j[1]) not in teams.values():
                            name = j[4].split("<")[0].replace(">", "").strip()
                            teams[name] = base_url + j[3]
        else:
            print("unsuccessful request!")
            print("status code:",response.status_code)
    file = "teams.json"
    with open(file, "w") as f:
        json.dump(teams, f)
    print("Saving json")

get_team_urls()

with open("teams.json", "r") as f:
    teams = json.load(f)

    print(dt.datetime.now(),"Downloading web pages...")
    for team in teams:
        response = requests.get(teams[team], headers=user_agent)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        save_name = teams[team].split("/")[4] + ".html"
        rdx_str = team

        with open(os.path.join("teams/",save_name), "w") as file:
            file.write(str(soup))
        print(dt.datetime.now(),rdx_str,"Saved:",save_name,end="\r")
        time.sleep(0.1)

    print(dt.datetime.now(),"Done")
