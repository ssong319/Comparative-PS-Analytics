import csv
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
        year = row[3]
        polity_score = row[4]
        #test code
        country = Country(country_code=country_code, country_name=country_name)
        db.session.add(country)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_polity_scores()
