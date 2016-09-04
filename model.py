from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = "countries"

    country_name = db.Column(db.String(50), primary_key=True)
    country_code = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return "<Country country_code=%s country_name=%s> \n" % (self.country_code, self.country_name)


class Indicators(db.Model):
    __tablename__ = "indicators"

    indicator_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_name = db.Column(db.String(50), db.ForeignKey('countries.country_name'))
    year = db.Column(db.Integer, nullable=False)
    polity = db.Column(db.Integer, nullable=True)
    gdp_per_cap = db.Column(db.Integer, nullable=True, default=None)
    eodb = db.Column(db.Integer, nullable=True, default=None)
    pol_stability = db.Column(db.Numeric, nullable=True, default=None)
    unemployment = db.Column(db.Integer, nullable=True, default=None)
    #ordering by descending order makes it easier to find the most recent values for each metric later on
    country = db.relationship('Country', backref=db.backref("indicators", order_by="desc(Indicators.year)"))

    def __repr__(self):
        return "<Indicators indicator_id=%s country_name=%s year=%s polity=%s eodb=%s pol_stability=%s gdp_per_cap=%s unemployment=%s> \n" % (self.indicator_id, self.country_name, self.year, self.polity, self.eodb, self.pol_stability, self.gdp_per_cap, self.unemployment)


class News(db.Model):
    __tablename__ = "news"

    news_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_name = db.Column(db.String(100), db.ForeignKey('countries.country_name'))
    title = db.Column(db.String(400), nullable=False)
    snippet = db.Column(db.Text(), nullable=True)
    url = db.Column(db.Text(), nullable=True)
    year = db.Column(db.String(50), nullable=False)
    country = db.relationship('Country', backref=db.backref("news"))

    def __repr__(self):
        return "<News news_id=%s country_name=%s year=%s title=%s url=%s snippet=%s> \n" % (self.news_id, self.country_name, self.year, self.title, self.url, self.snippet)


def fake_data():
    """Create some example data to use for testing purposes"""

    Country.query.delete()
    Indicators.query.delete()

    shakespeare = Country(country_name='Shakespeare', country_code='shk')
    mars = Country(country_name='Mars', country_code='mrs')

    shakespeare_metrics1 = Indicators(country_name='Shakespeare', year=2121, polity=10, gdp_per_cap=500000)
    shakespeare_metrics2 = Indicators(country_name='Shakespeare', year=2122, polity=10, gdp_per_cap=500001)
    shakespeare_metrics3 = Indicators(country_name='Shakespeare', year=2123, polity=10, gdp_per_cap=500002)

    mars_metrics1 = Indicators(country_name='Mars', year=2040, polity=-9, gdp_per_cap=400500)
    mars_metrics2 = Indicators(country_name='Mars', year=2041, polity=-10, gdp_per_cap=400000)
    mars_metrics3 = Indicators(country_name='Mars', year=2042, polity=-9, gdp_per_cap=400300)


    db.session.add_all([shakespeare, mars, shakespeare_metrics1, shakespeare_metrics2, shakespeare_metrics3, mars_metrics1, mars_metrics2, mars_metrics3])
    db.session.commit()



###
def connect_to_db(app, db_uri="postgresql:///pemetrics"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
