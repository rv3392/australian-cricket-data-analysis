class Bowler:
    def __init__(self, name : str = "", overs : str = "", maidens : int = 0, runs : int = 0,
            wickets : int = 0, profile_link : str = ""):
        self.name : str = name
        self.overs : str = overs
        self.maidens : int = maidens
        self.runs : int = runs
        self.wickets : int = wickets
        self.profile_link : str = profile_link

    def get_as_dataframe_row(self):
        return ({"Name" : self.name, "Overs": self.overs, 
                "Maidens": self.maidens, "Runs" : self.runs, 
                "Wickets": self.wickets, "Bowler Profile" : self.profile_link})

    def create_bowler_from_html(bowler_html):
        data = bowler_html.find_all("td")
        return Bowler(data[0].text, data[2].text, int(data[3].text),
                int(data[4].text), int(data[5].text), data[0].find("a")["href"])

    def __str__(self):
        return ("Bowler(" + "Name:" + self.name + ",Overs:" + self.overs +
                ",Maidens:" + str(self.maidens) + ",Runs:" + str(self.runs) + 
                ",Wickets:" + str(self.wickets) + ")")