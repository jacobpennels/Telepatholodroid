from flask import render_template
from app import app
from flask import request

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/view/<imgid>')
def view(imgid):
    return render_template('view.html', img=imgid)

