from jinja2 import StrictUndefined
from flask import Flask, request, render_template
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
    max_metrics = {}

    #list of indicator obj
    country_one = Country.query.get(selection_one.title()).indicators
    country_two = Country.query.get(selection_two.title()).indicators

    def find_max_values(country):
        country_name = country[1].country_name
        max_metrics[country_name] = {}

        metrics = ['polity', 'gdp_per_cap', 'eodb', 'pol_stability', 'unemployment']

        def find_max_metric(ind_objs, str_metric):
            for i in ind_objs:
                year = i.year
                attr_value = getattr(i, str_metric)
                if attr_value:
                    break
            max_metrics[country_name][str_metric] = [year, attr_value]

        for m in metrics:
            find_max_metric(country, m)

    find_max_values(country_one)
    find_max_values(country_two)


    # def find_max_metric(ind_objs, str_metric):
    #     for i in ind_objs:
    #         year = i.year
    #         attr_value = getattr(i, str_metric)
    #         if attr_value:
    #             break

    #     max_metrics
        #max_metrics[str_metric] = [year, attr_value]

    #test = find_max_values(country_one)

    return render_template("profile.html", max_metrics=max_metrics)


if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
