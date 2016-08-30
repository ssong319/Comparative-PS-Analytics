from jinja2 import StrictUndefined
from flask import Flask, request, render_template, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Country, Indicators, News
import os
import requests


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
    country_one_indicators = Country.query.get(selection_one).indicators
    session["first_country"] = selection_one

    country_two_indicators = Country.query.get(selection_two).indicators
    session["second_country"] = selection_two

    def insert_recent_values(ind_list):
        """obtains recent values and stores them in recent_metrics dictionary

        This function obtains the most recent values for each metric for each country and stores them in the recent_metrics variable. recent_metrics is a dictionary with country name as the key and a dictionary as the value. The nested dictionary has the name of the metric as the key and a list (with the year as the first element and the corresponding value as the second element) as the value
        """
        country_name = ind_list[1].country_name
        recent_metrics[country_name] = {}

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

@app.route('/metrics')
def metric_page():
    """Display metric page information"""

    return render_template("metrics.html")

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
        'borderColor': "rgba(69,50,137,1)",
        'borderCapStyle': 'round',
        'borderJoinStyle': 'miter',
        'pointBorderColor': "rgba(69,50,137,1)",
        'pointBackgroundColor': "rgba(69,50,137,1)",
        'pointBorderWidth': 1,
        'pointHoverRadius': 5,
        'pointHoverBackgroundColor': "rgba(69,50,137,1)",
        'pointHoverBorderColor': "rgba(69,50,137,1)",
        'pointHoverBorderWidth': 2,
        'pointRadius': 0.5,
        'pointHitRadius': 5,
        'data': data_c1,
        },
        {
            'label': session["second_country"],
            'fill': False,
            'lineTension': 0,
            'borderColor': "rgba(37,115,55,1)",
            'borderCapStyle': 'round',
            'borderJoinStyle': 'miter',
            'pointBorderColor': "rgba(37,115,55,1)",
            'pointBackgroundColor': "rgba(37,115,55,1)",
            'pointBorderWidth': 1,
            'pointHoverRadius': 5,
            'pointHoverBackgroundColor': "rgba(37,115,55,1)",
            'pointHoverBorderColor': "rgba(37,115,55,1)",
            'pointHoverBorderWidth': 2,
            'pointRadius': 0.5,
            'pointHitRadius': 5,
            'data': data_c2,
        }]}

    return jsonify(polity_data)

@app.route('/gdp.json')
def get_gdp_data():
    """Return gdp per cap data with corresponding year and polity score"""
    #var dataset = [[year, gdp, polity, index], [year, gdp, polity, index]...]
    #index is not necessary to create the graphs but comes in handy with the news feature later on
    country1_name = session["first_country"]
    country2_name = session["second_country"]

    dataset1 = []
    dataset2 = []
    #countries_gdps key would be name of country, and value would be dataset
    countries_gdps = {}
    country1_ind = Country.query.get(country1_name).indicators
    country2_ind = Country.query.get(country2_name).indicators

    for c in country1_ind:
        #only add to dataset if there is a gdp data
        if c.gdp_per_cap:
            year1 = c.year
            gdp_per_cap1 = c.gdp_per_cap
            if c.polity or c.polity == 0:
                polity_score1 = c.polity
            else:
                polity_score1 = 999
            dataset1.append([year1, gdp_per_cap1, polity_score1, 1])

    for d in country2_ind:
        #only add to dataset if there is a gdp data
        if d.gdp_per_cap:
            year2 = d.year
            gdp_per_cap2 = d.gdp_per_cap
            if d.polity or d.polity == 0:
                polity_score2 = d.polity
            else:
                polity_score2 = 999
            dataset2.append([year2, gdp_per_cap2, polity_score2, 2])

    countries_gdps[country1_name] = dataset1
    countries_gdps[country2_name] = dataset2

    return jsonify(countries_gdps)


@app.route('/news', methods=['POST'])
def get_news_data():
    """Get relevant search results given country name and year clicked"""

    # debug = 0

    # #js prop becomes key in request.form dict
    # #index is a string of "1" or "2"
    # y = request.form.get('year')
    # index = request.form.get('country_index')
    # search_results = {}

    # if index == "1":
    #     country_name = session["first_country"]
    # elif index == "2":
    #     country_name = session["second_country"]

    # key = os.environ['BING_SEARCH_KEY']
    # #Ex: Brazil in 2015, Argentina in 2015...
    # topic = country_name + ' in ' + y
    # search_results['tagline'] = topic

    # #already_clicked will return an empty list if user has not clicked yet, if user has, will return a list of news obj
    # already_clicked = News.query.filter(News.country_name == country_name, News.year == y).all()

    # if not already_clicked:

    #     debug += 1

    #     payload = {'q': topic, 'responseFilter': 'Webpages', 'mkt': 'en-us'}
    #     headers = {'Ocp-Apim-Subscription-Key': key}
    #     #'https://api.cognitive.microsoft.com/bing/v5.0/news/search'
    #     r = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/search', params=payload, headers=headers)

    #     all_results = r.json()

    #     print all_results

    #     #webpages is a list of dicts so w is each dict
    #     webpages = all_results['webPages']['value']

    #     for w in webpages:
    #         title = w['name'].encode('ascii', 'ignore')

    #         if w['url']:
    #             url = w['url'].encode('ascii', 'ignore')
    #         else:
    #             url = None

    #         #taking out snippet for now
    #         if w['snippet']:
    #             snippet = w['snippet'].encode('ascii', 'ignore')
    #         else:
    #             snippet = None

    #         article = News(title=title, country_name=country_name, year=y, url=url, snippet=snippet)
    #         print article
    #         db.session.add(article)

    #     db.session.commit()

    #     fetch = News.query.filter(News.country_name == country_name, News.year == y).all()

    #     if fetch:
    #         for f in fetch:
    #             search_results[f.news_id] = {'title': f.title, 'url': f.url, 'snippet': f.snippet}

    # else:
    #     for a in already_clicked:
    #         search_results[a.news_id] = {'title': a.title, 'url': a.url, 'snippet': a.snippet}

    # return jsonify(search_results)


    #test code
    return jsonify({})









if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
