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
    r = requests.get('http://api.worldbank.org/countries/all/indicators/NY.GDP.PCAP.CD?per_page=14784&format=json')
    gdp_per_cap = r.json()
    #list with dicts containing gdp info
    gdp_per_cap_list = gdp_per_cap[1]

    for i in gdp_per_cap_list:
        country_name = i["country"]["value"]
        year = int(i["date"])

        if i["value"] is not None:
            value = float(i["value"])
        else:
            value = None

        #.first() gets first record, returns none if none found so you can do an if statement
        fetch = Indicators.query.filter(Indicators.country_name == country_name, Indicators.year == year).first()

        if fetch:
            fetch.gdp_per_cap = value

    db.session.commit()






if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_polity_scores()
    add_gdp()
