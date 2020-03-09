# Bertelt Braaksma - s2568217
# extracts rider information from html-files in /riders directory
# outputs json with dict[rider_name] with another dict as value

from bs4 import BeautifulSoup
import os
import requests
import simplejson as json

riders = dict()
months = {"January": "01", "February": "02", "March": "03",
          "April" : "04", "May" : "05", "June" : "06", "July" : "07",
          "August" : "08", "September" : "09", "October" : "10",
          "November" : "11", "December" : "12"}

for fname in os.listdir("riders/"):
    with open(os.path.join("riders/",fname), "r") as file:
        page = file.read()
        soup = BeautifulSoup(page, "lxml")
        rider = str(soup.find("title").text.encode("utf-8").decode())
        riders[rider] = dict()

        pob, height, weight = None, None, None

        try:
            team = soup.find("span", class_="red").text
        except AttributeError:
            team = None

        bs = [b for b in soup.findAll("b")]
        for b in bs:
            if b.string.strip() == "Date of birth:":
                dob_day = b.next_sibling.strip()
                dob_my = b.next_sibling.next_sibling.next_sibling.split()
                dob_month = months[dob_my[0]]
                dob_year = dob_my[1]
                dob_str = "{}-{}-{}".format(dob_year, dob_month, dob_day)
            if b.string.strip() == "Height:":
                height = float(b.next_sibling.split()[0])
            if b.string.strip() == "Weight:":
                weight = float(b.next_sibling.split()[0])
            if b.string.strip() == "Nationality:":
                nationality = b.next_sibling.next_sibling.next_sibling.string
            if b.string.strip() == "Place of birth:":
                pob = b.next_sibling.next_sibling.string
                
        try:
            uci_rank = int(soup.find("div", {"class": "rdrStandings"}).text.split()[5])
        except (ValueError, AttributeError, IndexError) as e:
            uci_rank = None

        # define PSS specialty points
        scores = []
        for ultag in soup.find_all("ul", {"class": "pps"}):
            for litag in ultag.find_all("li"):
                scores.append(litag.text.split()[0])
    
        specialty = dict()
        try:
            specialty["classic"] = int(scores[0].replace("One", ""))
            specialty["gc"] = int(scores[1].replace("GC", ""))
            specialty["tt"] = int(scores[2].replace("Time", ""))
            specialty["sprinter"] = int(scores[3].replace("Sprint", ""))
            specialty["climber"] = int(scores[4].replace("Climber", ""))
        except ValueError:
            specialty = None

        riders[rider]["foaf:givenName"] = rider.split()[0]
        riders[rider]["foaf:surname"] = rider.split()[-1]
        riders[rider]["dbp:proteam"] = team
        riders[rider]["dbo:nationality"] = nationality
        riders[rider]["dbo:birthPlace"] = pob
        riders[rider]["dbo:birthDate"] = dob_str
        riders[rider]["dbo:height"] = height
        riders[rider]["dbo:weight"] = weight
        riders[rider]["uci_rank"] = uci_rank
        if specialty is not None:
            riders[rider]["dbp:ridertype"] = max(specialty, key=specialty.get)
        else:
            riders[rider]["dbp:ridertype"] = None

with open("riders.json", "w") as outfile:
    json.dump(riders, outfile)
