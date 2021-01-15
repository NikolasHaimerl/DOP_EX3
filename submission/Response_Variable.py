import requests
from bs4 import BeautifulSoup
import pandas as pd
DEFAULT_YEAR=2020
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
class ReponseVariableScraper:

    def __init__(self):
        self.year=DEFAULT_YEAR
        self.url_base=f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={self.year}&displayColumn=0"
        self.data={}
        self.european_countries=["Switzerland","Netherlands","Denmark",
"Austria","Luxembourg","Iceland","United Kingdom","Germany",
"Spain","Estonia","Sweden","Ireland","Slovenia","Lithuania",
        "Turkey","Czech Republic","Norway","Croatia",
        "France","Belgium","Portugal","Cyprus","Romania","Poland","Slovakia",
        "Latvia","Russia","Italy","Bulgaria","Serbia","Greece",
"Hungary","Ukraine"]

    def scrape_year(self,year,path=None):
        if year<2012 or year>2020: return
        if not path: path = f"../data/Quality_of_life_{year}"
        self.year = year
        self.url_base = f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={year}&displayColumn=0"
        if year==2012 or year ==2013:self.url_base = f"https://www.numbeo.com/quality-of-life/rankings.jsp?title={year}-Q1&displayColumn=0"

        self.__process_content()
        self.__save_data(path)

    def get_year(self,year,path=None):
        if not path: path = f"../data/Quality_of_life_{year}"
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
    def __filter_europe(self,df):
        df=df[df["Country"].isin(self.european_countries)]
        return df

    def __fill_nan(self,df):
        cols = df.columns
        n = df.to_numpy().reshape((len(cols),))
        x = cols[np.argwhere(~np.isnan(n))]
        y = n[np.argwhere(~np.isnan(n))]
        reg = LinearRegression().fit(x, y)
        miss = cols[np.argwhere(np.isnan(n))]
        pred = reg.predict(miss)
        n[np.argwhere(np.isnan(n))] = pred
        return n
    def get_interpolated_years(self):
        data = {}
        for year in range(2012, 2021):
            data[year] = self.get_year(year)
            data[year] = self.__filter_europe(data[year])
            data[year]["Rank"] = range(1, len(data[year]) + 1)
        all_cities = []
        for year in range(2012, 2021):
            all_cities.extend(data[year]["City"].unique())
        all_cities=list(set(all_cities))
        complete_data = pd.DataFrame(
            columns=["City", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"])
        complete_data["City"] = all_cities
        for year in range(2012, 2021):
            data_year = data[year]
            for city in all_cities:
                c = data_year["City"].to_list()
                if city in c:
                    g = data_year[data_year["City"] == city]["Quality of Life Index"].to_list()[0]
                    indx = complete_data[complete_data["City"] == city]
                    indx[str(year)] = float(g)
                    complete_data[complete_data["City"] == city] = indx
                else:
                    complete_data[complete_data["City"] == city][year] = np.nan
        res = []
        for city in all_cities:
            g = complete_data[complete_data["City"] == city]
            d = g[["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]]
            data_year = d
            data_year = pd.DataFrame(data_year, dtype='float32')
            data_year.interpolate(method='linear', axis=0, inplace=True)
            if data_year.isnull().values.any():
                data_year = self.__fill_nan(data_year)
            else:
                data_year = data_year.to_numpy()
            fill = pd.DataFrame(columns=["City", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"])
            fill["City"] = [city]
            fill[["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]] = data_year
            v = fill.values
            res.append(v[0])
            complete_data[complete_data["City"] == city] = fill
        complete_data.head()
        g = pd.DataFrame(res, columns=["City", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"])
        return g






if __name__=="__main__":
    scraper=ReponseVariableScraper()
    for year in range(2012,2021):
        scraper.scrape_year(year)
    g=scraper.get_interpolated_years()


