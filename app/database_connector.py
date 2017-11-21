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

            r = {"name": row[0], "type": row[2], "date_uploaded": row[7], "is_uploader": row[9] == usr_id, "has_edited": row[10] in slide_id, "uploader": row[10] + " " + row[11] + " " + row[12], "location": loc}
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
        self.execute_statement('INSERT INTO slides VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)', s_name, folder_name, data['type'], data['case_num'], data['consultant'], data['clinic_details'], data['prov_diag'], now_date, user_id)
        return [{"success": True, "s_name": s_name}, SlideInfo.SlideInfo(os.path.join(folder, folder_name), file.filename)]

    def delete_slide(self, r):
        print("Couldn't find folder, therefore deleting slide " + r[0] + ", in location " + r[1])
        self.execute_statement('DELETE FROM slides WHERE name=? and location=?', r[0], r[1])
