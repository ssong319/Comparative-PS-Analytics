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
        metric_description = ['Polity [+10 (full democracy) to -10 (full autocracy)]', 'GDP per capita (current US$)', 'Ease of doing business [1(best) to 189]', 'Political Stability [-2.5(weak) to 2.5(strong)]']

        def store_metric(ind_objs, str_metric):
            for i in ind_objs:
                year = i.year
                #getattr() takes an object and a str and returns the value of the obj attr whose attr name corresponds to the given str
                attr_value = getattr(i, str_metric)
                #if the attr_value actually has a value (ie not none), this would be the most recent value since the indicator obj list is sorted in descending order (see model.py).
                if attr_value:
                    break

            label = metric_description[metrics.index(str_metric)]
            recent_metrics[country_name][label] = [year, attr_value]

        for m in metrics:
            store_metric(ind_list, m)

    insert_recent_values(country_one_indicators)
    insert_recent_values(country_two_indicators)

    return render_template("profile.html", recent_metrics=recent_metrics, c1=selection_one, c2=selection_two)

@app.route('/polity-scores.json')
def get_polity_data():
    """Return polity data for line chart"""

    country1_ind = Country.query.get(session["first_country"]).indicators
    country2_ind = Country.query.get(session["second_country"]).indicators

    years = []
    #polity data for the first country
    data_c1 = []
    #polity data for the second country
    data_c2 = []

    #first scenario: country 2 is the longer time series. Then country 2's list needs to be truncated so that there is no years-to-score mismatch on the graph
    if len(country1_ind) < len(country2_ind):
        #years list will start with the earliest year that both countries have a polity value
        for c in country1_ind:
            years.append(c.year)
            data_c1.append(c.polity)

        #figure out how many more polity scores are in country 2 then truncate it. Since the lists are sorted by most recent year in the front, this list slice assignment will truncate the earliest years for country 2 in which polity scores for country 1 are nonexistent
        offset = len(country1_ind) - len(country2_ind)
        country2_ind = country2_ind[:offset]

        for d in country2_ind:
            data_c2.append(d.polity)

    #scenario: country 1 is the longer time series, same logic as the first
    elif len(country2_ind) < len(country1_ind):
        for c in country2_ind:
            years.append(c.year)
            data_c2.append(c.polity)

        offset = len(country2_ind) - len(country1_ind)
        country1_ind = country1_ind[:offset]

        for d in country1_ind:
            data_c1.append(d.polity)

    #if both countries have the same length, no truncation needed
    else:
        for c in country1_ind:
            years.append(c.year)
            data_c1.append(c.polity)

        for d in country2_ind:
            data_c2.append(d.polity)


    #list of objs are sorted by most recent year but we want to start from the earliest year on the graph
    years.reverse()
    data_c1.reverse()
    data_c2.reverse()

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

@app.route('/gdp.json')
def get_gdp_data():
    """Return gdp per cap data with corresponding year and polity score"""
#var dataset = [[year, gdp, polity], [year, gdp, polity]...]
    dataset1 = []
    dataset2 = []
    countries_gdps = {}
    country1_ind = Country.query.get(session["first_country"]).indicators
    country2_ind = Country.query.get(session["second_country"]).indicators

    for c in country1_ind:
        #only add to dataset if there is a gdp data
        if c.gdp_per_cap:
            year1 = c.year
            gdp_per_cap1 = c.gdp_per_cap
            polity_score1 = c.polity
            dataset1.append([year1, gdp_per_cap1, polity_score1])

    countries_gdps['one'] = dataset1

    for d in country2_ind:
        #only add to dataset if there is a gdp data
        if d.gdp_per_cap:
            year2 = d.year
            gdp_per_cap2 = d.gdp_per_cap
            polity_score2 = d.polity
            dataset2.append([year2, gdp_per_cap2, polity_score2])

    countries_gdps['two'] = dataset2

    return jsonify(countries_gdps)








if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
