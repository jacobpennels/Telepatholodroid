from flask import Flask
from flask import request, session, redirect, url_for

app = Flask(__name__)

from app import views

@app.route('/test')
def test():
    return "This is a test"