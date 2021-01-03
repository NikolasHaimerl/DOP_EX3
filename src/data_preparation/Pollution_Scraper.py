import requests
from bs4 import BeautifulSoup
import pandas as pd
DEFAULT_YEAR=2020
class ReponseVariableScraper:

    def __init__(self):
        self.year=DEFAULT_YEAR
        self.url_base=f"https://www.numbeo.com/pollution/region_rankings.jsp?title={self.year}&displayColumn=0&region=150"
        self.data={}

    def scrape_year(self,year,path=None):
        if year<2012 or year>2020: return
        if not path: path = f"../../data/Pollution_{year}"
        self.year = year
        self.url_base = f"https://www.numbeo.com/pollution/region_rankings.jsp?title={year}&region=150&displayColumn=0"
        if year==2012 or year ==2013:self.url_base = f"https://www.numbeo.com/pollution/region_rankings.jsp?title={year}-Q1&displayColumn=0&region=150"

        self.__process_content()
        self.__save_data(path)

    def get_year(self,year,path=None):
        if not path: path = f"../data/Pollution_{year}"
        try:
            df=pd.read_csv(path,header=0)
        except(FileNotFoundError):
            self.scrape_year(year)
            df=self.get_year(year)
        return df

    def __process_content(self):
        page = requests.get(self.url_base)
        soup = BeautifulSoup(page.content, "html.parser")
        tb = soup.find(id="t2")
        header = tb.find_all_next("th")
        headings = []
        for head in header:
            headings.extend(head.div.contents)
        body = tb.find_next("tbody").find_all("tr")
        ranks = []
        city = []
        qol = []
        rank = 1
        for row in body:
            content = row.find_all("td")
            ranks.append(rank)
            city.extend(content[1])
            qol.extend(content[2])
            rank+=1
        tupls = list(zip(ranks, city, qol))
        df = pd.DataFrame(tupls, columns=headings)
        cities = df["City"].map(lambda x: x.split(", ")[0])
        countries = df["City"].map(lambda x: x.split(", ")[1])
        df["City"] = cities
        df["Country"] = countries
        self.data[self.year]=df

    def __save_data(self,path):
        self.data[self.year].to_csv(path,header=True)


if __name__=="__main__":
    scraper=ReponseVariableScraper()
    for year in range(2012,2021):
        scraper.scrape_year(year)


