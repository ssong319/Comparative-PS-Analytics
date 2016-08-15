import csv
import requests
from model import Country, Indicators, connect_to_db, db
from server import app


def load_country_and_polity():
    """Creates country objects and indicator objects with polity scores

     This function creates a country object for each country in the polity dataset and creates indicators objects for each country and assigns them a polity score. Each country has an indicator object for each year it has a polity score in the dataset. Time series span roughly from time of state formation to 2015
    """

    #format of csv file: ccode, scode, country, year, polityScore
    f = open("seed_data/polity.csv")
    #csv.reader() returns a reader object which will iterate over lines in the given csvfile
    csv_f = csv.reader(f)

    for row in csv_f:
        country_code = row[1]
        country_name = row[2]
        year = int(row[3])
        polity_score = row[4]

        # This condition is needed to account for cases where there are no polity score values otherwise we'll get an invalid literal error
        if polity_score is not '':
            polity_score = int(polity_score)
        else:
            polity_score = None

        # this query is to check if a country obj for a particular country has been created already
        check = Country.query.filter_by(country_name=country_name).all()

        #if the country obj has not already been created, create one
        if check == []:
            country = Country(country_code=country_code, country_name=country_name)

        #create an indicator obj and give it a polity score for that country, for that year
        indicators = Indicators(country_name=country_name, year=year, polity=polity_score)

        db.session.add(country)
        db.session.add(indicators)

    db.session.commit()

def load_gdp():
    """loads gdp per capita info to indicators objects

    This function submits a get request to the World Bank for gdp per capita info, fetches the appropriate indicator obj by querying for country name and year, then assigns the gdp per cap value to that obj accordingly
    """
    #aside: if instead want to create a function that can take any world bank obj can access attr via getattr(object, attrname)
    #setattr(object, attrname, value) where attrname can be a string that corresponds to the attr

    #this api call gets all gdp per cap info for all countries for all available years
    r = requests.get('http://api.worldbank.org/countries/all/indicators/NY.GDP.PCAP.CD?per_page=14784&format=json')

    gdp_info = r.json()
    #gdp_per_cap_list is a list with dicts containing gdp info for each country per year
    gdp_per_cap_list = gdp_info[1]

    for g in gdp_per_cap_list:
        country_name = g["country"]["value"]
        year = int(g["date"])

        if g["value"] is not None:
            value = float(g["value"])

            #.first() gets first record, returns none if none found
            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

            if fetch:
                fetch.gdp_per_cap = value

    db.session.commit()

def load_ease_of_business():
    """loads ease of doing business (eodb) score to indicators objects

    This function submits a get request to the World Bank for ease of doing business scores for all countries, fetches the indicators object for 2015 and assigns the eodb score to that obj. Unlike gdp per cap, we are not storing a time series data for this metric, only the most recent eodb score
    """

    r = requests.get('http://api.worldbank.org/countries/all/indicators/IC.BUS.EASE.XQ?format=json&per_page=16848')

    ease_of_business_info = r.json()

    ease_of_business_ranks = ease_of_business_info[1]

    for e in ease_of_business_ranks:
        #this condition is needed since ease_of_business_ranks contains eodb scores for years other than 2015, but we only want the 2015 score
        if e["date"] == "2015":
            year = 2015
            country_name = e["country"]["value"]

            if e["value"] is not None:
                value = int(float(e["value"]))

                fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

                if fetch:
                    fetch.eodb = value

    db.session.commit()

def load_pol_stability():
    """loads political stability score to indicators objects

    Parses the political stability dataset, fetches the appropriate indicators object and assigns the political stability metric. This is also a time series
    """
    f = open("seed_data/polstbcsv.csv")

    #format of csv file: country_name, score1, score2.... (for each row)
    csv_f = csv.reader(f)
    #these years correspond to the pol stab score for each row in the csv file
    years = [1996, 1998, 2000, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]

    for row in csv_f:
        #Grab the name of the country. title() is needed since country name is in all caps (otherwise it will not query properly).
        country_name = row[0].title()
        row = row[1:]

        #we want to loop over a list of numbers so we can query by a particular year in the years list
        for i in range(16):
        #account for #N/A values. row[i][1] checks the 'N' part for each item. the len() part is needed since some values are single digits, without it, it will throw an index error
            if len(row[i]) > 1 and row[i][1].isalpha():
                value = None
            else:
                value = float(row[i])

            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == years[i]).first()

            if fetch:
                fetch.pol_stability = value

#this funct not working error: ValueError: Unterminated string starting at: line 1 column 1708246 (char 1708245)
def load_unemployment():
    """loads long-term unemployment metrics to indicators objects

    This function submit a get request to the World Bank for long-term unemployment (as percentage of total unemployment) metrics, fetches the corresponding indicators object and assigns the metric. This is a time series
    """

    r = requests.get("http://api.worldbank.org/countries/all/indicators/SL.UEM.LTRM.ZS?format=json&per_page=14784")

    unemployment_info = r.json()

    unemployment_list = unemployment_info[1]

    for u in unemployment_list:
        country_name = u["country"]["value"]
        year = int(u["date"])

        if u["value"] is not None:
            value = float(u["value"])

            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

            if fetch:
                fetch.unemployment = value

    db.session.commit()




if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_country_and_polity()
    load_gdp()
    load_ease_of_business()
    load_pol_stability()
    #load_unemployment()
