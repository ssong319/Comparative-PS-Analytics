from jinja2 import StrictUndefined
from flask import Flask, request, render_template, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Country, Indicators


app = Flask(__name__)

app.secret_key = "Axx3553fsdabb"

app.jinja_env.undefined = StrictUndefined

app.jinja_env.auto_reload = True

@app.route('/')
def index():
    """Show homepage."""

    return render_template("homepage.html")

@app.route('/profile')
def show_profile():
    """Show country profile page"""

    selection_one = request.args.get("countryone")
    selection_two = request.args.get("countrytwo")
    recent_metrics = {}

    #obtain the list of indicator objs for each selected country

    #maybe store this info in a session so we have access at other routes
    if selection_one:
        country_one_indicators = Country.query.get(selection_one.title()).indicators
        session["first_country"] = country_one_indicators[0].country_name
    if selection_two:
        country_two_indicators = Country.query.get(selection_two.title()).indicators
        session["second_country"] = country_two_indicators[0].country_name

    def insert_recent_values(ind_list):
        """obtains recent values and stores them in recent_metrics dictionary

        This function obtains the most recent values for each metric for each country and stores them in the recent_metrics variable. recent_metrics is a dictionary with country name as the key and a dictionary as the value. The nested dictionary has the name of the metric as the key and a list (with the year as the first element and the corresponding value as the second element) as the value
        """
        country_name = ind_list[1].country_name
        recent_metrics[country_name] = {}

        #took out unemployment for now - load funct not working
        metrics = ['polity', 'gdp_per_cap', 'eodb', 'pol_stability']

        def store_metric(ind_objs, str_metric):
            for i in ind_objs:
                year = i.year
                #getattr() takes an object and a str and returns the value of the obj attr whose attr name corresponds to the given str
                attr_value = getattr(i, str_metric)
                #if the attr_value actually has a value (ie not none), this would be the most recent value since the indicator obj list is sorted in descending order (see model.py).
                if attr_value:
                    break
            recent_metrics[country_name][str_metric] = [year, attr_value]

        for m in metrics:
            store_metric(ind_list, m)

    insert_recent_values(country_one_indicators)
    insert_recent_values(country_two_indicators)

    return render_template("profile.html", recent_metrics=recent_metrics)

@app.route('/polity-scores.json')
def get_polity_data():
    """Return polity data for line chart"""

    country1_ind = Country.query.get(session["first_country"]).indicators
    country2_ind = Country.query.get(session["second_country"]).indicators

    years = []
    data_c1 = []
    data_c2 = []

    if len(country1_ind) < len(country2_ind):
        for c in country1_ind:
            years.append(c.year)
    else:
        for c in country2_ind:
            years.append(c.year)

    for d in country1_ind:
        #note: consider whether chart js can handle null values
        data_c1.append(d.polity)

    for p in country2_ind:
        data_c2.append(p.polity)

    years.reverse()
    data_c1.reverse()
    data_c2.reverse()

    #!!!bug - ex US vs Italy - US starts at 1800 and Italy starts later, Italy's polity score points will be off with the years on the x-axis since you start with the other country. Temporary fix - changed line 79 from > to < to start with the later country.

    #polity_data should store scores for both countries, in the datasets key have an array with two dictionaries of polity scores, one per country
    polity_data = {'labels': years, 'datasets': [{
        'label': session["first_country"],
        'fill': False,
        'lineTension': 0,
        'borderColor': "rgba(209,24,24,1)",
        'borderCapStyle': 'round',
        'borderJoinStyle': 'miter',
        'pointBorderColor': "rgba(209,24,24,1)",
        'pointBackgroundColor': "#fff",
        'pointBorderWidth': 1,
        'pointHoverRadius': 5,
        'pointHoverBackgroundColor': "rgba(75,192,192,1)",
        'pointHoverBorderColor': "rgba(220,220,220,1)",
        'pointHoverBorderWidth': 2,
        'pointRadius': 1,
        'pointHitRadius': 10,
        'data': data_c1,
        },
        {
            'label': session["second_country"],
            'fill': False,
            'lineTension': 0,
            'borderColor': "rgba(24,24,209,1)",
            'borderCapStyle': 'round',
            'borderJoinStyle': 'miter',
            'pointBorderColor': "rgba(24,24,209,1)",
            'pointBackgroundColor': "#fff",
            'pointBorderWidth': 1,
            'pointHoverRadius': 5,
            'pointHoverBackgroundColor': "rgba(75,192,192,1)",
            'pointHoverBorderColor': "rgba(220,220,220,1)",
            'pointHoverBorderWidth': 2,
            'pointRadius': 1,
            'pointHitRadius': 10,
            'data': data_c2,
        }]}

    return jsonify(polity_data)


if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
