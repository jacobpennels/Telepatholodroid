from flask import Flask
from flask import request, session, redirect, url_for, render_template, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import signal, sys
import threading
import binascii, os
import queue
import time
import openslide
import base64
from openslide import deepzoom
from PIL import Image, ImageDraw
from json import dumps
import io

from app import database_connector, SlideInfo, GenerateReport

global app
global login_manager
running = False
global db_lock
db_lock = threading.Lock()  # Must acquire before working on database
global db
global upload_folder
global allowed_extensions
global s_queue
global image_handler
global gp
global path

def init_app():
    global login_manager, running, db, upload_folder, allowed_extensions, s_queue, image_handler, gp, path
    s_queue = queue.Queue()
    running = True
    upload_folder = os.path.abspath('app/static/uploads')
    print(upload_folder)
    allowed_extensions = set(['jpg', 'png', 'jp2', 'svs'])
    app = Flask(__name__)

    login_manager = LoginManager()
    login_manager.init_app(app)
    app.config['UPLOAD_FOLDER'] = upload_folder
    path = os.path.abspath('app/database.db')
    db = database_connector.DatabaseConnector(path)
    db.up_folder = upload_folder

    image_handler = ImageHandler()
    image_handler.start()
    gp = GenerateReport.GenerateReport('app/static/temp')

    def interrupt():
        global running
        running = False
        #print(running)

        image_handler.join()
        db.close()
        print("Quitting App")

    def signal_handler(signal, frame):
        global running
        interrupt()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    running = True
    return app

def confirm_is_uploaded(name):
    db_lock.acquire()
    db.confirm_upload(name)
    db_lock.release()

class ImageHandler(threading.Thread):  # TODO implement image handling
    def run(self):
        global s_queue
        global running

        #print("Running is set to " + str(running))
        self.get_images()

    def get_images(self):
        print("Beginning image handling")
        global running
        while(running):
            try:
                slide = s_queue.get(timeout=1)
                print(slide)
                self.handle_image(slide)
            except queue.Empty:
                pass

        time.sleep(1)  # Stop the thread looping too hard

        print("Image handler shutting down")

    def handle_image(self, slide):
        global path, db_lock
        if(not isinstance(slide, SlideInfo.SlideInfo)):
            return False
        print(slide.dir)
        print(slide.file)
        osr = openslide.OpenSlide(slide.dir + "/" + slide.file)
        self.create_thumbnail(osr.get_thumbnail((150, 150)), slide.dir)
        self.create_files(osr, slide.dir)
        db_lock.acquire()
        db_temp = database_connector.DatabaseConnector(path)
        db_temp.confirm_upload(slide.name)
        db_temp.close()
        db_lock.release()

    def create_thumbnail(self, img, s_dir): # Creates a 150px x 150px image as a thumbnail
        size = (max(img.size),) * 2
        layer = Image.new('RGB', size, (255, 255, 255))
        layer.paste(img, tuple(map(lambda x: (x[0] - x[1]) // 2, zip(size, img.size))))

        layer.save(s_dir + "/thumb.png")

    def create_files(self, o, d):
        # Creates the relevant file hierachy for the given image
        # Is a lengthy process so may take a while to complete - need way of telling this to the user
        dz = deepzoom.DeepZoomGenerator(o, tile_size=256, overlap=0)

        for i, l in enumerate(dz.level_tiles):
            dir_name = d + '/level_' + str(i)
            os.makedirs(dir_name)
            #print(i)
            tile_info = {}
            for x in range(l[0]):
                for y in range(l[1]):
                    img = dz.get_tile(i, (x, y))
                    img.save(dir_name + '/tile_' + str(x) + '_' + str(y) + '.png')
                    tile_info['tile_' + str(x) + '_' + str(y)] = dz.get_tile_dimensions(i, (x, y))

            with open(dir_name + '/dim.json', 'w') as f:
                f.write(dumps(tile_info))

        print("The slide is uploaded")
        # Create dimensions file for use in
        info = {}
        for i, a in enumerate(dz.level_dimensions):
            tiles = dz.level_tiles[i]
            info['level_' + str(i)] = [a[0], a[1], tiles[0], tiles[1]]

        with open(d + "/dimensions.json", 'w') as f:
            f.write(dumps(info))


def allow_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


app = init_app()
app.secret_key = binascii.hexlify(os.urandom(24))

from app import views, user, forms
from app.forms import LoginForm, RegistrationForm, UploadForm, FeedbackForm

login_manager.login_view = 'index'


# Used by Flask-Login

@login_manager.user_loader
def load_user(user_id):
    # print("user id is " + str(user_id))
    global db, db_lock
    db_lock.acquire()
    val = db.get_user_by_id(user_id)
    db_lock.release()
    return val


# These views handle AJAX calls

@app.route('/login', methods=['POST', 'GET'])
def login():
    global db, db_lock
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate_on_submit():
            # Check the credentials are correct
            user_email = request.form['email']
            user_pword = request.form['password']
            db_lock.acquire()
            is_valid = db.log_user_in(user_email, user_pword)
            db_lock.release()
            if not is_valid:
                return render_template('index.html', loginform=LoginForm(), regform=RegistrationForm())

            # Get the user object
            db_lock.acquire()
            usr = db.get_user_by_email(user_email)
            db_lock.release()
            # Configure user
            usr.authenticated = True
            usr.active = True
            # Log them in
            login_user(usr)
            print("User logged in")

            return redirect(form.redirect_target or url_for('home'))
        return render_template('index.html', loginform=LoginForm(), regform=RegistrationForm())
    else:
        return render_template('index.html', loginform=LoginForm(), regform=RegistrationForm())


@app.route('/register', methods=['POST', 'GET'])
def register():
    global db, db_lock
    if request.method == 'POST':
        form = RegistrationForm(request.form)
        if form.validate_on_submit():
            print("Validated")
            # Add new user to database
            db_lock.acquire()
            usr = db.register_user(request.form)
            db_lock.release()

            # Log the new user in
            usr.authenticated = True
            usr.active = True
            login_user(usr)
            print("User logged in")

            return redirect(form.redirect_target or url_for('home'))
        print(form.data)
        return render_template('index.html', loginform=LoginForm(), regform=form, success="something")
    else:
        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/get_slides', methods=['POST'])
@login_required
def get_slides():
    global db, db_lock
    data = request.get_json()
    print("Recieved a ajax request")
    try:
        print("Cancer type is: " + data['cancer_type'])
    except TypeError:
        print("No cancer defined")
    if (current_user.is_authenticated):
        usr_id = current_user.user_id
    db_lock.acquire()
    results = db.get_slide_info_by_category(data['cancer_type'], usr_id)
    db_lock.release()
    return jsonify(results)


@app.route('/change_account_setting', methods=['POST'])
@login_required
def change_account_setting():
    global db, db_lock
    data = request.get_json()
    usr_id = None
    if (current_user.is_authenticated):
        usr_id = current_user.user_id
    db_lock.acquire()
    success = db.change_account_detail(data, usr_id)
    db_lock.release()
    return jsonify(success)


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    global db, db_lock
    data = request.get_json()
    usr_id = None
    if (current_user.is_authenticated):
        usr_id = current_user.user_id
    db_lock.acquire()
    success = db.change_password(data, usr_id)
    db_lock.release()
    return jsonify(success)


@app.route('/accept_upload', methods=['POST'])
@login_required
def accept_upload():
    global db, db_lock, s_queue
    if request.method == 'POST':
        form = UploadForm()
        if form.validate_on_submit():
            file = form.u_file.data
            # print(file.filename)
            if form.name.data == '':
                print("no filename")
                return jsonify({"success": False})
            if file and allow_filename(file.filename):
                db_lock.acquire()
                if (not current_user.is_authenticated):
                    return False
                res = db.add_new_slide(form, app.config['UPLOAD_FOLDER'], current_user.user_id)
                db_lock.release()
                s_queue.put(res[1])
                return jsonify(res[0])

                # print("Failed option 1")
                # print("Failed option 2")

    return redirect(url_for('home'))


@app.route('/save_annotation', methods=['POST'])
@login_required
def save_annotation():
    data = request.get_json()
    print("name: " + str(data['name']) + ", description: " + str(data['anno_description']))
    user_id = None
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    success = db.add_new_annotation(data, user_id)
    db_lock.release()

    return jsonify(success)

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    global gp
    data = request.get_json()
    print(data['slide_data'])
    print(data['anno_data'])
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    print("Slide id is " + str(data['slide_data'][-1]))
    slide_info = db.get_slide_data_by_id(data['slide_data'][-1], user_id)
    anno_info = db.get_annotations(data['slide_data'][-1])
    db_lock.release()
    print(slide_info)
    annotations = []
    for a in anno_info:
        if(a[-1] in data['anno_data']):
            annotations.append(a)

    #print(annotations)

    report = gp.create_and_save_report(str(slide_info[1]), slide_info, annotations)
    return jsonify({"success": True, "location": report})

@app.route('/update_slide_info', methods=['POST'])
@login_required
def update_slide_info():
    global db, db_lock
    data = request.get_json()
    attr = data['attr']
    db_lock.acquire()
    if(attr == 0): # Update provisional diagnosis
        info = jsonify(db.update_prov_diag(data['slide_id'], data['info']))
    else:
        info = jsonify(db.update_clin_details(data['slide_id'], data['info']))

    db_lock.release()
    return info

@app.route('/add_new_permission', methods=['POST'])
@login_required
def add_new_permission():
    global db, db_lock
    data = request.get_json()
    email = data['email']
    slide_id = data['slide_id']
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    result = db.add_new_permissions(email, user_id, slide_id)
    db_lock.release()
    return jsonify(result)

@app.route('/remove_permission', methods=['POST'])
@login_required
def remove_permission():
    global db, db_lock
    data = request.get_json()
    if (current_user.is_authenticated):
        user_id = current_user.user_id
    db_lock.acquire()
    result = db.remove_permissions(user_id, data['id'], data['slide_id'])
    db_lock.release()
    return jsonify(result)

@app.route('/save_feedback', methods=['POST'])
@login_required
def save_feedback():
    form = FeedbackForm(request.form)
    if(current_user.is_authenticated):
        user_id = current_user.user_id

    db_lock.acquire()
    db.save_feedback(request.form['bug_title'], request.form['bug_description'], user_id)
    db_lock.release()

    return redirect(url_for('feedback'))





