import sqlite3
from app import user, SlideInfo
import datetime
import os
from passlib.hash import sha256_crypt
import hashlib
import datetime
from flask import url_for

class DatabaseConnector:

    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        self.up_folder = None

    def close(self):
        self.conn.close()

    def execute_statement(self, statement, *args):
        self.c.execute(statement, tuple(args))
        self.conn.commit()

    def execute_query(self, statement, *args):
        self.c.execute(statement, tuple(args))
        return self.c.fetchall()

    def run_script(self, filename):
        with open(filename, 'r') as f:
            query = f.read()
        self.c.executescript(query)
        self.conn.commit()

    def create_user(self, row):
        # creates a user object from a row from users table
        if(row == None):
            return None
        return user.User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[8])

    def get_user_by_id(self, user_id):
        row= self.execute_query('select * from users where id=?', user_id)[0]
        return self.create_user(row)

    def get_user_by_email(self, user_email):
        row = self.execute_query('select * from users where email=?', user_email)[0]
        return self.create_user(row)

    def log_user_in(self, user_email, user_pword):
        print(self.filename)
        try:
            row = self.execute_query('select password from users where email=?', user_email)[0]
        except IndexError: # User doesn't exist
            return False
        return sha256_crypt.verify(user_pword,  row[0])

    def register_user(self, u):
        # Sort through data into suitable order and then add the user to the database
        self.execute_statement('insert into users values (?, ?, ?, ?, ?, ?, ?, ?, NULL )',\
                               u['title'], u['fname'], u['lname'], u['email1'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), u['institute'], u['country'], sha256_crypt.encrypt(u['pword1']))
        return self.get_user_by_email(u['email1'])

    def get_slide_info_by_category(self, category, usr_id):
        results = []
        rows = self.execute_query('select * from (slides s join users u on s.uploader_id = u.id) where type=?', category)
        slides_accessed = self.execute_query('select slide_id from user_to_slides where user_id=?', usr_id)
        slide_id = [x[0] for x in slides_accessed]
        print(slide_id)
        for row in rows:
            if(row[1] == "none"):
                loc = url_for('static', filename="image/thumb1.jpg")
            else:
                if(os.path.isdir(self.up_folder + "/" + row[1])):
                    if(os.path.isfile(self.up_folder + "/" + row[1] + "/thumb.jpg")):
                        loc = url_for('static', filename='uploads/' + row[1] + '/thumb.jpg')
                    else:
                        loc = url_for('static', filename='uploads/' + row[1] + '/thumb.png')
                else:
                    self.delete_slide(row)
                    continue
            print(row[10])
            query = self.execute_query('SELECT user_id FROM permissions WHERE slide_id=?', row[10])
            print(query)
            if(not usr_id in [x[0] for x in query]):
                print("PERMISSION DENIED")
                continue
            anno = self.execute_query('SELECT * FROM annotations WHERE slide_id=?', row[10])
            num_annotations = len(anno)
            # name0 | location1 | type2 | case_num3 | consultant4 | clinic_details5 | prov_diag6 | dateuploaded7 | viewable8 | uploader_id9 | id10 | title11 | fname12 | lname13 | email14 | date_joined15 | institute16 | country17 | password18 | id19
            r = {"name": row[0], "type": row[2], "date_uploaded": row[7], "is_uploader": row[9] == usr_id, "has_edited": row[10] in slide_id, "uploader": row[11] + " " + row[12] + " " + row[13], "location": loc, "viewable": row[8], "slide_id" : row[10], "num_anno" : num_annotations}
            results.append(r)
        return results

    def change_account_detail(self, data, usr_id):
        form = data['detail']
        d = data['data']
        print(d)
        if(form == "name_form"):
            name = str(d).split(" ")
            title, fname, lname = str(name[0]), str(name[1]), str(" ".join(name[2:]))
            self.execute_statement('UPDATE users SET title=?, fname=?, lname=? WHERE id=?', title, fname, lname, usr_id)
        elif(form == "institute_form"):
            self.execute_statement('UPDATE users SET institute=? WHERE id=?', d, usr_id)
        elif(form == "country_form"):
            self.execute_statement('UPDATE users SET country=? WHERE id=?', d, usr_id)
        elif(form == "email_form"):
            self.execute_statement('UPDATE users SET email=? WHERE id=?', d, usr_id)
        else:
            return {"success": False}

        return {"success": True}

    def change_password(self, data, usr_id):
        user_pword = self.execute_query('select password from users where id=?', usr_id)[0]
        if(sha256_crypt.verify(str(data['old_password']), user_pword[0])):
            # Correct password
            self.execute_statement('UPDATE users SET password=? WHERE id=?', sha256_crypt.encrypt(data['new_password']), usr_id)
            return {"success": True}
        return {"success": False}

    def check_folder(self, dname, folder):  # Checks the file doesn't exist, and if does, returns a suitable name
        fname = dname
        i = 0
        while (os.path.isdir(os.path.join(folder, dname))):
            print("Current name, changing")
            fname = dname + "_" + str(i)
            i += 1

        return fname

    def check_file_name(self, name):
        current_names = [x[0] for x in self.execute_query('select name from slides')]
        fname = name
        i = 0
        while(fname in current_names):
            fname = name + "_" + str(i)
            i += 1

        return fname

    def add_new_slide(self, form, folder, user_id):
        print(form.data['name'])
        file = form.u_file.data
        filename, ext = file.filename.rsplit('.')
        s_name = self.check_file_name(form.data['name'])

        # Create a nice random folder name
        h = hashlib.md5()
        now_date = datetime.datetime.now().__str__()
        h.update(str.encode(filename + now_date))
        folder_name = self.check_folder(h.hexdigest()[:10], folder)
        print(folder_name)

        os.makedirs(os.path.join(folder, folder_name))
        file.save(os.path.join(os.path.join(folder, folder_name), filename + "." + ext))
        data = form.data
        self.execute_statement('INSERT INTO slides VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)', s_name, folder_name, data['type'], data['case_num'], data['consultant'], "", "", now_date, 0, user_id)
        slide_id = self.c.lastrowid
        self.execute_statement('INSERT INTO permissions VALUES (?, ?)', slide_id, user_id)
        return [{"success": True, "s_name": s_name}, SlideInfo.SlideInfo(os.path.join(folder, folder_name), file.filename, s_name)]

    def delete_slide(self, r):
        print("Couldn't find folder, therefore deleting slide " + r[0] + ", in location " + r[1])
        self.execute_statement('DELETE FROM slides WHERE name=? and location=?', r[0], r[1])

    def get_slide_data(self, name, user_id):
        query = self.execute_query('SELECT * FROM slides WHERE name=?', name)[0] # Should be only one result
        permission = self.execute_query('SELECT user_id FROM permissions WHERE  slide_id=?', query[-1])
        if (user_id in [x[0] for x in permission]):
            print("PERMISSION DENIED")
            return query
        else:
            return None

    def get_slide_data_by_id(self, slide_id, user_id):
        query = self.execute_query('SELECT * FROM slides WHERE id=?', slide_id)[0]
        permission = self.execute_query('SELECT user_id FROM permissions WHERE  slide_id=?', slide_id)
        if (user_id in [x[0] for x in permission]):
            print("PERMISSION DENIED")
            return query
        else:
            return None

    def add_new_annotation(self, data, user_id):
        temp = [] # Turn the points into a list of points
        for a in data['points']:
            for b in a:
                temp.append(str(b))

        points = ",".join(temp)
        print(points)
        self.execute_statement('INSERT INTO annotations VALUES(?, ?, ?, ?, ?, ?, ?, NULL)', data['name'], data['anno_description'], data['colour'], points, data['image'], user_id, data['slide_id'])
        return {"success": True}

    def get_annotations(self, slide_id):
        return self.execute_query('SELECT * FROM annotations WHERE slide_id=?', slide_id)

    def confirm_upload(self, s_name):
        self.execute_statement('UPDATE slides SET viewable=1 WHERE name=?', s_name)

    def update_prov_diag(self, slide_id, info):
        self.execute_statement('UPDATE slides SET prov_diag=? WHERE id=?', info, slide_id)
        return {"success" : True}

    def update_clin_details(self, slide_id, info):
        self.execute_statement('UPDATE slides SET clinic_details=? WHERE id=?', info, slide_id)
        return {"success" : True}

    def record_slide_access(self, slide_id, user_id):
        has_accessed = self.execute_query('SELECT * FROM user_to_slides WHERE (user_id=? AND slide_id=?)', user_id, slide_id)
        if(len(has_accessed) > 0): # this user has accessed this slide before
            self.execute_statement('UPDATE user_to_slides SET accessed=? WHERE (user_id=? AND slide_id=?)', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id, slide_id)
        else:
            self.execute_statement('INSERT INTO user_to_slides VALUES(?, ?, ?)', user_id, slide_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_permitted_users(self, slideid, user_id):
        query = self.execute_query('SELECT u.title, u.fname, u.lname, u.id, u.email from (permissions p join users u on u.id=p.user_id) where p.slide_id=?', slideid)
        users = []
        for row in query:
            if(user_id != row[3]):
                result = {"name" : str(row[0]) + " " + str(row[1]) + " " + str(row[2]), "email" : row[4], "id": row[3]}
                users.append(result)

        return users

    def add_new_permissions(self, email, user_id, slide_id):
        slide = [x[0] for x in self.execute_query('SELECT uploader_id FROM slides WHERE id=?', slide_id)]
        if(not user_id in slide):
            return {"success" : 0}

        user = self.execute_query('SELECT title, fname, lname, id FROM users WHERE email=?', email)
        print(user)
        if(len(user) > 0): # the user exists
            user = user[0]
            if(len(self.execute_query('SELECT * FROM permissions WHERE (user_id=? AND slide_id=?)', user[-1], slide_id)) == 0):
                self.execute_statement('INSERT INTO permissions VALUES(?, ?)', slide_id, user[-1])
                return {"name" : str(user[0]) + " " + str(user[1]) + " " + str(user[2]), "email" : email, "id" : user[-1], "success" : 1}
            else: # User already added
                return {"success" : 2}

        return {"success" : 0}

    def remove_permissions(self, user_id, p_id, slide_id):
        slide = [x[0] for x in self.execute_query('SELECT uploader_id FROM slides WHERE id=?', slide_id)]
        if (not user_id in slide): # User doesn't have permission to be changing these permissions
            print("This user doesn't have permission to edit this")
            return {"success": False}

        self.execute_statement('DELETE FROM permissions WHERE user_id=? AND slide_id=?', p_id, slide_id)
        return {"success": True}