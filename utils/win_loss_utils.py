import requests
import pandas as pd
import bs4
import datetime
import dateutil

HOME_AWAY_URL = "https://stats.espncricinfo.com/ci/engine/team/2.html?class=1;filter=advanced;orderby=start;spanmax2=31+Dec+2019;spanmin2=01+Jan+1990;spanval2=span;template=results;type=team;view=results"
HOME_URL = "https://stats.espncricinfo.com/ci/engine/team/2.html?class=1;filter=advanced;home_or_away=1;orderby=start;spanmax1=31+Dec+2019;spanmin1=01+Jan+1990;spanval1=span;template=results;type=team;view=results"
AWAY_URL = "https://stats.espncricinfo.com/ci/engine/team/2.html?class=1;filter=advanced;home_or_away=2;home_or_away=3;orderby=start;spanmax1=31+Dec+2019;spanmin1=01+Jan+1990;spanval1=span;template=results;type=team;view=results"

'''
    Saving, parsing and loading data.
'''

def get_html_data(data_url : str) -> str:
    data_request = requests.get(data_url)
    data_html = data_request.text

    return data_html

def parse_html_data(data_html : str) -> pd.DataFrame:
    html = bs4.BeautifulSoup(data_html, "html.parser")
    tables = html.find_all(name="table")
    win_loss_table : str = str(tables[3])

    data : pd.DataFrame = pd.read_html(win_loss_table, index_col=7)[0]
    data = data.rename(columns={"Unnamed: 8": "Global Test ID"})
    data["Scorecard Link"] = _get_scorecard_links(win_loss_table)
    data["Ground Link"] = _get_ground_links(win_loss_table)
    data = data.drop(columns="Unnamed: 4")

    return data

def _get_scorecard_links(table_html):
    table = bs4.BeautifulSoup(table_html, "html.parser")
    scorecard_links = []

    for row in table.tbody.find_all("tr"):
        cells = row.find_all("td")
        scoresheet_link = cells[8].find("a")["href"]

        scorecard_links.append(scoresheet_link)
        
    return scorecard_links

def _get_ground_links(table_html):
    table = bs4.BeautifulSoup(table_html, "html.parser")
    ground_links = []

    for row in table.tbody.find_all("tr"):
        cells = row.find_all("td")
        ground_link = cells[6].find("a")["href"]

        ground_links.append(ground_link)
        
    return ground_links

def save_data():
    data_html = get_html_data(HOME_AWAY_URL)
    data = parse_html_data(data_html)
    data.to_csv("data/australia-test-summary-1990-2020-all.csv")

    data_html = get_html_data(HOME_URL)
    data = parse_html_data(data_html)
    data.to_csv("data/australia-test-summary-1990-2020-home.csv")

    data_html = get_html_data(AWAY_URL)
    data = parse_html_data(data_html)
    data.to_csv("data/australia-test-summary-1990-2020-away.csv")

def load_data():
    '''Loads and returns the data from CSV files.

        save_data() (or the CSV files from save_data() must exist in the folder
        data/) must be called before load_data() can be called.

        Returns:
            a tuple containing (all_data, home_data, away_data)
    '''
    all_data = pd.read_csv("data/australia-test-summary-1990-2020-all.csv", parse_dates=True)
    home_data = pd.read_csv("data/australia-test-summary-1990-2020-home.csv", parse_dates=True)
    away_data = pd.read_csv("data/australia-test-summary-1990-2020-away.csv", parse_dates=True)

    return (all_data, home_data, away_data)

'''
    Complex data transformations into better formats
'''

def get_rolling_win_percentage(years : int, data : pd.DataFrame) -> pd.DataFrame:
    new_data = data[["Start Date", "Result"]]
    rolling_data = (pd.get_dummies(data[["Start Date", "Result"]])
            .rolling(str(years * 365) + "D", on="Start Date").sum())
    rolling_data[["Result_won", "Result_lost", "Result_draw"]] = (
            rolling_data[["Result_won", "Result_lost", "Result_draw"]]
            .div(rolling_data[["Result_won", "Result_lost", "Result_draw"]]
            .sum(axis=1), axis=0))
    
    rolling_data = rolling_data.rename(
            columns={"Result_won": "Win", "Result_lost": "Loss", 
            "Result_draw": "Draw", "Start Date": "Time"})

    cutoff = [1990 + i for i in range(years)]
    rolling_data = rolling_data[~rolling_data["Time"].dt.year.isin(cutoff)]

    rolling_data = rolling_data.set_index("Time")
    return rolling_data

def new_get_rolling_win_percentage(years : int, data : pd.DataFrame) -> pd.DataFrame:
    new_data = dict()

    new_data["date"] = dict()
    new_data["won"] = dict()
    new_data["lost"] = dict()
    new_data["draw"] = dict()

    start_date = datetime.datetime(day=1, month=1, year=1990)
    for month in range(360):
        new_data["date"][month] = start_date + dateutil.relativedelta.relativedelta(months=month)
        new_data["won"][month] = 0
        new_data["lost"][month] = 0
        new_data["draw"][month] = 0

    for row in data[["Start Date", "Result"]].iterrows():
        i = (row[1]["Start Date"].year - 1990) * 12 + row[1]["Start Date"].month - 1
        if row[1]["Result"] == "won":
            new_data["won"][i] += 1
        if row[1]["Result"] == "lost":
            new_data["lost"][i] += 1
        if row[1]["Result"] == "draw":
            new_data["draw"][i] += 1
    new_data = pd.DataFrame.from_dict(new_data)

    rolling_data = new_data.rolling(str(years * 365) + "D", on="date").sum()
    rolling_data[["won", "lost", "draw"]] = (rolling_data[["won", "lost", "draw"]].div(rolling_data[["won", "lost", "draw"]].sum(axis=1), axis=0))
    rolling_data = rolling_data.fillna(0)

    rolling_data = rolling_data.rename(columns={"date":"Time", "won":"Win", "lost":"Loss", "draw":"Draw"})
    
    print(rolling_data)

    cutoff = [1990 + i for i in range(years)]
    rolling_data = rolling_data[~rolling_data["Time"].dt.year.isin(cutoff)]

    rolling_data = rolling_data.set_index("Time")
    return rolling_data

def debug():
    save_data()
    load_data()

if __name__ == "__main__":
    debug()