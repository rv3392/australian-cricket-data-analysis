import bs4
import pandas as pd
import requests

from utils import win_loss_utils

def get_ground_details(ground_url):    
    data_request = requests.get("https://www.espncricinfo.com" + ground_url)
    data_html = data_request.text

    data = bs4.BeautifulSoup(data_html)
    location = data.find(name="a", href="/ci/content/ground/index.html").text
    country = location.split(" / ")[1].strip("\t").strip("\n")

    return country

def save_data():
    all_data, home_data, away_data = win_loss_utils.load_data()
    
    grounds = all_data[["Ground", "Ground Link"]]
    grounds = grounds.drop_duplicates()
    grounds["Country"] = grounds["Ground Link"].apply(
            lambda link: get_ground_details(link))
    grounds.sort_values(by=["Country"])

    grounds.to_csv("data/grounds.csv", index=False)

def load_data():
    grounds = pd.read_csv("data/grounds.csv")
    return grounds

if __name__ == "__main__":
    save_data()
