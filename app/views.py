from flask import render_template, redirect, url_for
from flask_login import login_required
import threading
from app import app, forms, user
from app import db_lock, db
import os
from flask import request
import json

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
    annotation_form = forms.AnnotationForm()
    if(imgid == None):
        return redirect('home')
    db_lock.acquire()
    temp = db.get_slide_data_by_id(imgid) # Get location of file
    data = temp[1]
    slide_id = temp[-1]
    anno = db.get_annotations(slide_id)
    db_lock.release()
    annotations = []
    for v in anno:
        temp = []
        for a in v:
            temp.append(a)
        annotations.append(temp)

    for a in annotations:
        points = a[3]
        p_array = []

        temp = []
        print(points.split(","))
        for p in points.split(","):
            if(len(temp) < 2):
                temp.append(float(p))
            else:
                p_array.append(temp)
                temp = [float(p)]
        p_array.append(temp)
        a[3] = p_array

    print(annotations)

    dimensions = ""
    with open(os.path.abspath('app/static/uploads/' + data + '/dimensions.json'), 'r') as f:
        dimensions = f.readline()
        #dimensions = json.dumps(dimensions)
        print(dimensions)

    return render_template('viewimg.html', imgid=imgid, slide_id = slide_id, loc=str(url_for('static', filename="uploads") + "/" + data), dimensions=dimensions, form = annotation_form, anno=json.dumps(annotations))

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

@app.route('/reviewimg/<imgid>')
@login_required
def reviewimg(imgid=None):
    db_lock.acquire()
    data = db.get_slide_data_by_id(imgid)
    anno = db.get_annotations(data[-1])
    db_lock.release()
    print(anno)
    return render_template('reviewimg.html', data=data, data_j=json.dumps(data), anno=anno, anno_j=json.dumps(anno))





