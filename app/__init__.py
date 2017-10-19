from flask import Flask
from flask import request, session, redirect, url_for

app = Flask(__name__)

from app import views


# These views handle AJAX calls
@app.route('/test')
def test():
    return "This is a test"

@app.route('/login', methods=['POST'])
def login():
    if(request.method == 'POST'):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))
