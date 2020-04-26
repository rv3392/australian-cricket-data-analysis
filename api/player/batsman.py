from bs4 import BeautifulSoup

class Batsman:
    def __init__(self, name : str, runs : int, balls : int, profile_link : str):
        self.name : str = name
        self.runs : int = runs
        self.balls : int = balls
        self.profile_link : str = profile_link

    def __str__(self):
        return ("Batsman(Name:" + str(self.name) + 
                ",Runs:" + str(self.runs) + 
                ",Balls:" + str(self.balls) + ")")

    def get_as_dataframe_row(self):
        return ({"Name" : self.name, "Runs" : self.runs, "Balls" : self.balls, "Batsman Profile" : self.profile_link})

    def create_batsman_from_html(batsman_html):
        name = (batsman_html
                .find("div", {"class":"cell batsmen"})
                .find("a").text)

        profile_link = batsman_html.find("div", {"class":"cell batsmen"}).find("a")["href"]
        
        cell_runs = batsman_html.find_all("div", {"class":"cell runs"})
        if len(cell_runs) >= 2:
            runs = cell_runs[0].text
            balls = cell_runs[1].text
        else:
            runs = 0
            balls = 0

        return Batsman(name, runs, balls, profile_link)

