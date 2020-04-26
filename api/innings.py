from bs4 import BeautifulSoup
import pandas as pd

from typing import Dict

from .player.batsman import Batsman
from .player.bowler import Bowler

class Innings:
    def __init__(self, batsmen, bowlers):
        self._batsmen : List[Batsman] = batsmen
        self._bowlers : List[Bowler] = bowlers

    def __str__(self):
        return ("Inning(Batsmen:" + str([str(batsman) for batsman in self._batsmen]) +
                ",Bowlers:" + str([str(bowler) for bowler in self._bowlers]) + ")")

    def save(self, match_id, innings_num, dates, country):
        batting = pd.DataFrame(columns=["Country", "Date", "Name", "Runs", "Balls", "Batsman Profile"])
        bowling = pd.DataFrame(columns=["Country", "Date", "Name", "Overs", "Maidens", "Runs", "Wickets", "Bowler Profile"])
        dates = dates.strip(" ")
        for batsman in self._batsmen:
            row = batsman.get_as_dataframe_row()
            row["Country"] = country
            row["Date"] = dates
            batting = batting.append(row, ignore_index=True)

        for bowler in self._bowlers:
            row = bowler.get_as_dataframe_row()
            row["Country"] = country
            row["Date"] = dates
            bowling = bowling.append(row, ignore_index=True)

        batting.to_csv("matches/match-" + str(match_id) + "/inning-" + str(innings_num) + "-batting.csv", index=False)
        bowling.to_csv("matches/match-" + str(match_id) + "/inning-" + str(innings_num) + "-bowling.csv", index=False)

    def create_innings_from_html(inning_html):
        batsmen : List[Batsman] = []
        bowlers : List[Bowler] = []

        for batsman in inning_html.find_all("div", {"class":"wrap batsmen"}):
            batsmen.append(Batsman.create_batsman_from_html(batsman))

        for i, bowler in enumerate(inning_html.find(
                "div",{"class":"scorecard-section bowling"}).find_all("tr")):
            if i == 0:
                continue
            bowlers.append(Bowler.create_bowler_from_html(bowler))

        return Innings(batsmen=batsmen, bowlers=bowlers)