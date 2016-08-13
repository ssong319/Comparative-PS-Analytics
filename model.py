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
    pols = db.Column(db.Numeric, nullable=True, default=None)
    unemployment = db.Column(db.Integer, nullable=True, default=None)
    country = db.relationship('Country', backref=db.backref("indicators", order_by=year))

    def __repr__(self):
        return "<Indicators indicator_id=%s country_name=%s year=%s polity=%s eodb=%s pols=%s gdp_per_cap=%s unemployment=%s> \n" % (self.indicator_id, self.country_name, self.year, self.polity, self.eodb, self.pols, self.gdp_per_cap, self.unemployment)


###
def connect_to_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pemetrics'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
