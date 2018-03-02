from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
import threading
from app import app, forms, user
from app import db_lock, db, login_manager
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
@app.route('/home/<imgid>')
@login_required
def home(imgid = None):
    if(imgid == None):
        print(current_user.user_id)
        return render_template('home.html')
    else:
        if(current_user.is_authenticated):
            user_id = current_user.user_id
        else:
            return redirect('index')

        db_lock.acquire()
        data = db.get_current_slide(imgid, user_id)
        db_lock.release()
        if(data['success'] == False):
            return render_template('home.html')
        print("Got slide id, focusing on it")
        return render_template('home.html', data=data)

@app.route('/viewimg/<imgid>')
@app.route('/viewimg/<imgid>/<annotation>')
@login_required
def viewimg(imgid=None, annotation = None):
    annotation_form = forms.AnnotationForm()
    if(imgid == None):
        return redirect('home')

    if(annotation == None):
        show_annotation = -1
    else:
        show_annotation = annotation
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    temp_1 = db.get_slide_data_by_id(imgid, user_id) # Get location of file
    data = temp_1[1]
    slide_id = temp_1[-1]
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
        for p in points.split("|"):
            sub = []
            temp = []
            for c in p.split(","):
                if(len(temp) < 2):
                    temp.append(float(c))
                else:
                    sub.append(temp)
                    temp = [float(c)]
            p_array.append(sub)

        print(len(p_array))

        a[3] = p_array

    print(annotations)

    is_uploader = False
    if(temp_1[9] == user_id):
        print("Is uploader")
        is_uploader = True

    dimensions = ""
    with open(os.path.abspath('app/static/uploads/' + data + '/dimensions.json'), 'r') as f:
        dimensions = f.readline()
        #dimensions = json.dumps(dimensions)
        print(dimensions)
    db_lock.acquire()
    db.record_slide_access(slide_id, current_user.user_id)
    db_lock.release()
    return render_template('viewimg.html', user_id=user_id, imgid=imgid, slide_id = slide_id, loc=str(url_for('static', filename="uploads") + "/" + data), dimensions=dimensions, form = annotation_form, anno=json.dumps(annotations), sa = show_annotation, is_uploader=is_uploader)

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
    if (current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    data = db.get_slide_data_by_id(imgid, user_id)
    anno = db.get_annotations(data[-1])
    db_lock.release()
    print(anno)
    return render_template('reviewimg.html', data=data, data_j=json.dumps(data), anno=anno, anno_j=json.dumps(anno))

@app.route('/testcanvas')
def testcanvas():
    return render_template('testcanvas.html')

@app.route('/manage_permissions/<slideid>')
@login_required
def manage_permissions(slideid):
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    slide = db.get_slide_data_by_id(slideid, user_id)
    permitted_users = db.get_permitted_users(slideid, user_id)
    db_lock.release()

    if(user_id != slide[-2]): # means only the uploader can access the permissions page
        return redirect('home')

    return render_template('manage_permissions.html', slide=slide, pu=permitted_users, pujs=json.dumps(permitted_users))

@app.route('/feedback')
@login_required
def feedback():
    form = forms.FeedbackForm()
    return render_template('feedback.html', feedback = form)









