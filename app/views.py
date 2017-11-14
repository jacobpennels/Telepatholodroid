from flask import render_template, redirect, url_for
from flask_login import login_required
import threading
from app import app, forms, user
from app import db_lock, db
import os
from flask import request

@app.route('/')
def index():
    login_form = forms.LoginForm()
    registration_form = forms.RegistrationForm()
    registration_form.country.default = 'GB'
    registration_form.process()
    return render_template("index.html", loginform = login_form, regform = registration_form)

@app.route('/home')
@login_required
def home():
    slide_list = [1,2,3,4,5,6,7,8,9,10]
    return render_template('home.html', slide_list = slide_list)

@app.route('/viewimg/<imgid>')
@login_required
def viewimg(imgid=None):
    return render_template('viewimg.html', imgid=imgid)

@app.route('/accountsettings')
@login_required
def account_settings():
    return render_template('accountsettings.html')

@app.route('/uploadimage')
@login_required
def uploadimage():
    u_form = forms.UploadForm()
    u_form.u_file.default = 0
    return render_template('uploadimage.html', form=u_form)





