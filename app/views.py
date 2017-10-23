from flask import render_template, redirect, url_for
from app import app
import os
from flask import request

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/viewimg/<int:imgid>')
def viewimg(imgid=None):
    return render_template('viewimg.html', imgid=imgid)





