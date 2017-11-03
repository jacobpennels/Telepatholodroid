from app import database_connector

class User:

    def __init__(self, title, fname, lname, email, date_joined, institute, country, user_id):
        self.user_id = user_id
        self.title = title
        self.fname = fname
        self.lname = lname
        self.email = email
        self.date_joined = date_joined
        self.institute = institute
        self.authenticated = False
        self.active = False
        self.country = country

    # Methods needed by Flask-Login
    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False # No anonymous users

    def get_id(self):
        return self.user_id

    # Class methods


