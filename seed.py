import csv
import requests
from model import Country, Indicators, connect_to_db, db
from server import app

#todo: write comments, figure out Country and Indicator instant.

def load_polity_scores():
#format of csv file: ccode, scode, country, year, polityScore

    f = open("seed_data/polity.csv")
    #csv.reader() returns a reader object which will iterate over lines in the given csvfile
    csv_f = csv.reader(f)

    for row in csv_f:
        country_code = row[1]
        country_name = row[2]
        year = int(row[3])
        polity_score = row[4]

        # some have no polity score values (empty str with no spaces) thus we need to do this otherwise we'll get invalid literal error
        if polity_score is not '':
            polity_score = int(polity_score)
        else:
            polity_score = None

        # create country obj if it hasn't been created already
        # seems to work ok
        check = Country.query.filter_by(country_name=country_name).all()
        #create the country first
        if check == []:
            country = Country(country_code=country_code, country_name=country_name)

        indicators = Indicators(country_name=country_name, year=year, polity=polity_score)

        db.session.add(country)
        db.session.add(indicators)

    db.session.commit()

def add_gdp():
    #aside: if instead want to create a function that can take any world bank obj can access attr via getattr(object, attrname)
    #setattr(object, attrname, value) where attrname can be a string that corresponds to the attr


    r = requests.get('http://api.worldbank.org/countries/all/indicators/NY.GDP.PCAP.CD?per_page=14784&format=json')
    #create a different var name here this is a obj attr so it's confusing
    gdp_info = r.json()
    #list with dicts containing gdp info
    gdp_per_cap_list = gdp_info[1]

    for i in gdp_per_cap_list:
        country_name = i["country"]["value"]
        year = int(i["date"])

        if i["value"] is not None:
            value = float(i["value"])

        #.first() gets first record, returns none if none found so you can do an if statement
            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

            if fetch:
                fetch.gdp_per_cap = value

    db.session.commit()

def load_ease_of_business():
    r = requests.get('http://api.worldbank.org/countries/all/indicators/IC.BUS.EASE.XQ?format=json&per_page=16848')

    ease_of_business_info = r.json()

    ease_of_business_ranks = ease_of_business_info[1]


    for e in ease_of_business_ranks:
        if e["date"] == "2015":
            year = 2015
            country_name = e["country"]["value"]

            if e["value"] is not None:
                value = int(float(e["value"]))

                fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

                if fetch:
                    fetch.eodb = value

    db.session.commit()

def load_pol_stabiliy():
    f = open("seed_data/polstbcsv.csv")
    #csv.reader() returns a reader object which will iterate over lines in the given csvfile. Thus you don't need to use split
    csv_f = csv.reader(f)

    years = [1996, 1998, 2000, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]

    for row in csv_f:
        country_name = row[0].title()
        row = row[1:]
        # [score_96, score_98, score_00, score_02, score_03, score_04, score_05, score_06, score_07, score_08, score_09, score_10, score_11, score_12, score_13, score_14] = row
        for i in range(16):  #list of [0...15] 16 total
        #clean for #N/A values. row[i][1] checks the N part for each item
            print country_name
            if len(row[i]) > 1 and row[i][1].isalpha():
                value = None
            else:
                value = float(row[i])

            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == years[i]).first()

            if fetch:
                fetch.pols = value


def load_unemployment():
    r = requests.get('http://api.worldbank.org/countries/all/indicators/SL.UEM.LTRM.ZS?format=json&per_page=16848')

    unemployment_info = r.json()

    unemployment_list = unemployment_info[1]

    for u in unemployment_list:
        country_name = u["country"]["value"]
        year = int(u["date"])

        if u["value"] is not None:
            value = float(u["value"])

        #.first() gets first record, returns none if none found so you can do an if statement
            fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

            if fetch:
                fetch.unemployment = value

    db.session.commit()




if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_polity_scores()
    #add_gdp()
    #load_ease_of_business()
    #load_pol_stabiliy()
    load_unemployment()
