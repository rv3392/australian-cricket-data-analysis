from typing import List

import os
import requests
from bs4 import BeautifulSoup

from .innings import Innings

class Match:
    def __init__(self, match_url, match_id):
        self._url : str = match_url
        self._id : str = match_id
        self._innings : List[Innings] = []
        self._country_innings : List[str] = []

        self.match_description : str
        self.dates : str

        match_html = self._get_match_html(match_url)
        self._parse_data(match_html)

    def _get_match_html(self, match_url):
        match_request = requests.get(
                "https://www.espncricinfo.com" + match_url)
        match_html = match_request.text
        return match_html

    def load_data(self):
        pass

    def _parse_data(self, match_html : str):
        match_soup = BeautifulSoup(match_html, features="lxml")
        for i in range(4):
            inning = match_soup.find(name="div", id="gp-inning-0" + str(i))
            if inning == None:
                break
            self._innings.append(Innings.create_innings_from_html(inning))
            country = match_soup.find("a", {"href": "#gp-inning-0" + str(i)})\
                    .find("h2").text
            country = country.replace(" 1st Innings", "").replace(" 2nd Innings", "")
            self._country_innings.append(country)

        overview = match_soup.find("div", {"class" : "cscore_info-overview"}).text.split(",")

        self.match_description = overview[0] + " " + overview[1]
        self.dates = overview[2]

    def save(self):
        if not os.path.exists("matches/match-" + str(self._id)):
            os.makedirs("matches/match-" + str(self._id))
        for inning_num, inning in enumerate(self._innings):
            inning.save(match_id=self._id, innings_num=inning_num,
                    dates=self.dates, country=self._country_innings[inning_num])

    def __str__(self):
        return ("Scorecard(Innings:" + 
                str([str(inning) for inning in self._innings]) + ")")

def main():
    match = Match(match_url="/ci/engine/match/63530.html", match_id="63530")
    match.save()

if __name__ == "__main__":
    main()