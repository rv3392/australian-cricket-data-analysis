import requests
import pandas as pd
import bs4

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
    data["Scorecard Link"] = _get_links(win_loss_table)
    data = data.drop(columns="Unnamed: 4")

    return data

def _get_links(table_html):
    table = bs4.BeautifulSoup(table_html, "html.parser")
    scoresheet_links = []

    for row in table.tbody.find_all("tr"):
        cells = row.find_all("td")
        scoresheet_link = cells[8].find("a")["href"]

        scoresheet_links.append(scoresheet_link)
        
    return scoresheet_links

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

def debug():
    save_data()
    load_data()

if __name__ == "__main__":
    debug()