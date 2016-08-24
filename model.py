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
    country_name = db.Column(db.String(50), db.ForeignKey('countries.country_name'))
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(600), nullable=True)
    date = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(400), nullable=True)
    image_url = db.Column(db.String(400), nullable=True)
    source = db.Column(db.String(50), nullable=True)
    sent_score = db.Column(db.Integer, nullable=True)



###
def connect_to_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pemetrics'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
