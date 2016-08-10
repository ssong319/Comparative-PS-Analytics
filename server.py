from flask import Flask, render_template
from model import connect_to_db, db, Country, Indicators

app = Flask(__name__)
