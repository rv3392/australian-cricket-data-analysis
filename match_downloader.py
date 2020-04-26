from api.scorecard import Match
import pandas as pd

home_data = pd.read_csv("data/australia-test-summary-1990-2020-all.csv")
links = list(home_data["Scorecard Link"])
ids = list(home_data["Scorecard Link"].apply(lambda x: x.split("/")[-1].split(".")[0]))

for i in range(len(links)):
    print("Saving Match #" + str(i) + ":" + str(ids[i]))

    match = Match(match_url=links[i], match_id=ids[i])
    match.save()