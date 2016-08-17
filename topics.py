#import requests

#all topic indicators and information about them
#r = requests.get('http://api.worldbank.org/indicators?per_page=16848&format=json')

#topics = r.json()

#list with dictionaries containing topic info
#list_of_topics = topics[1]

#show all topics in terminal
# for l in list_of_topics:
#     if l["name"]:
#         print l["name"]


#selected topics
#format of each k/v: id: {name: --, sourceNote: --}
#selected = {}

# selected["polity"] = {name: "Polity (score ranges from +10 (full democracy) to -10 (full autocracy))", sourceNote: "Data obtained from Center for Systemic Peace's Polity IV Project, Political Regime Characteristics and Transitions, 1800-2015, annual, cross-national, time-series and polity-case formats coding democratic and autocratic patterns of authority and regime changes in all independent countries with total population greater than 500,000 in 2015 (167 countries in 2015)"}

# selected["3.0.Gini"] = {name: "Gini Coefficient", sourceNote: "sourceNote":"The Gini coefficient is most common measure of inequality. It is based on the Lorenz curve, a cumulative frequency curve that compares the distribution of a specific variable (in this case, income) with the uniform distribution that represents equality. The Gini coefficient is bounded by 0 (indicating perfect equality of income) and 1, which means complete inequality. This calculation includes observations of 0 income."}

# selected["IC.BUS.EASE.XQ"] = {name: "Ease of doing business index (1=most business-friendly regulations)", sourceNote: "Ease of doing business ranks economies from 1 to 189, with first place being the best. A high ranking (a low numerical rank) means that the regulatory environment is conducive to business operation. The index averages the country's percentile rankings on 10 topics covered in the World Bank's Doing Business. The ranking on each topic is the simple average of the percentile rankings on its component indicators."}

#Estimate   Estimate of governance (ranges from approximately -2.5 (weak) to 2.5 (strong) governance performance)
