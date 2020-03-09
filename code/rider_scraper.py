# Bertelt Braaksma - s2568217
# downloads all rider pages for teams in the /teams directory
# files stored in /riders directory

from bs4 import BeautifulSoup
import datetime as dt
import glob
import numpy as np
import os
import requests
import simplejson as json
import time

user_agent = {"User-agent": "Mozilla/5.0"}

print("{} Getting urls".format(dt.datetime.now()))
urls = set()

with open("teams.json", "r") as f:
    teams = json.load(f)
    for team in teams:
        fname = teams[team].split("/")[4] + ".html"
        with open(os.path.join("teams/",fname), "r") as file:
            page = file.read()
            soup = BeautifulSoup(page, "lxml")
            riders = soup.findAll("a", {"class": "rider"})
            for rider in riders:
                urls.add("https://www.procyclingstats.com/" + rider.get("href"))

print("{} Number of riders: {}".format(dt.datetime.now(), len(urls)))

print(dt.datetime.now(),"Downloading web pages...")
for rdx, first_url in enumerate(urls):
    response = requests.get(first_url, headers=user_agent)
    page = response.text
    soup = BeautifulSoup(page, "lxml")
    save_name = first_url.split("/")[4] + ".html"

    with open(os.path.join("riders/",save_name), "w") as file:
        file.write(str(soup))
    print("{} Rider {}: {}".format(dt.datetime.now(), rdx+1, save_name))
    time.sleep(0.1)

print(dt.datetime.now(),"Done")
