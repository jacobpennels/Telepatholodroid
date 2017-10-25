from flask import render_template, redirect, url_for
from app import app
import os
from flask import request

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    slide_list = [1,2,3,4,5,6,7,8,9,10]
    return render_template('home.html', slide_list = slide_list)

@app.route('/viewimg/<int:imgid>')
def viewimg(imgid=None):
    return render_template('viewimg.html', imgid=imgid)

@app.route('/accountsettings')
def account_settings():
    return render_template('accountsettings.html')





