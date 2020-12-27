import requests
from bs4 import BeautifulSoup
import pandas as pd
#
# year=2019
# url_base=f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={year}&displayColumn=0"
# page=requests.get(url_base)
# soup=BeautifulSoup(page.content,"html.parser")
# tb=soup.find(id="t2")
# header=tb.find_all_next("th")
# headings=[]
# for head in header:
#     headings.extend(head.div.contents)
# print(headings)
#
# body=tb.find_next("tbody").find_all("tr")
# ranks=[]
# city=[]
# countries=[]
# qol=[]
# rank = 1
# for row in body:
#     content=row.find_all("td")
#     ranks.append(rank)
#     city.extend(content[1])
#     qol.extend(content[2])
#     rank+=1
# print(ranks)
# print(city)
# print(qol)
# tupls=list(zip(ranks,city,qol))
# df=pd.DataFrame(tupls,columns=headings)
# cities=df["City"].map(lambda x:x.split(",")[0])
# countries=df["City"].map(lambda x:x.split(",")[1])
# df["City"]=cities
# df["Country"]=countries
# print(df)

DEFAULT_YEAR=2020
class ReponseVariableScraper:

    def __init__(self):
        self.year=DEFAULT_YEAR
        self.url_base=f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={self.year}&displayColumn=0"
        self.data={}

    def scrape_year(self,year,path=None):
        if year<2012 or year>2020: return
        if not path: path = f"../data/Quality_of_life_{year}"
        self.year = year
        self.url_base = f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={year}&displayColumn=0"
        self.__process_content()
        self.__save_data(path)

    def get_year(self,year,path=None):
        if not path: path = f"../data/Quality_of_life_{year}"
        return pd.read_csv(path,header=0)

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
        tupls = list(zip(ranks, city, qol))
        df = pd.DataFrame(tupls, columns=headings)
        cities = df["City"].map(lambda x: x.split(",")[0])
        countries = df["City"].map(lambda x: x.split(",")[1])
        df["City"] = cities
        df["Country"] = countries
        self.data[self.year]=df

    def __save_data(self,path):
        self.data[self.year].to_csv(path,header=True)


if __name__=="__main___":
    scraper=ReponseVariableScraper()
    scraper.scrape_year(2012)

