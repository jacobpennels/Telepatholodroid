from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.fields import PasswordField, StringField, HiddenField, SelectField, TextField, FileField, TextAreaField
from wtforms import validators
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect
from werkzeug.exceptions import NotFound, HTTPException
from app import app

# collect countries for the select statement
from app import generate_countries

global country_list
country_list = generate_countries.GenerateCountries.get_countries()


# uk_position = country_list.index(('UK', 'United Kingdom'))

# This snippet protects the application from any nasty / malicious redirects
# Snippet courtesy of https://gist.github.com/brownhead/2964235
# Licensed under Unlicense
class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get("next") or request.referrer

        try:
            # Will raise an exception if no endpoint exists for the url
            app.create_url_adapter(request).match(self.next.data)
        except NotFound:
            self.next.data = ""
        except HTTPException:
            # Any other exceptions are harmless (I think)
            pass

    @property
    def redirect_target(self):
        return self.next.data


class LoginForm(RedirectForm):
    email = EmailField(validators=[validators.DataRequired(), validators.Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[validators.DataRequired()], render_kw={"placeholder": "Password"})


class RegistrationForm(RedirectForm):
    title = SelectField(u'Title <span class="star">*</span>',
                        choices=[('Dr', 'Dr'), ('Mr', 'Mr'), ('Miss', 'Miss'), ('Mrs', 'Mrs'), ('Ms', 'Ms')],
                        validators=[validators.DataRequired()], render_kw={'data-native-menu': 'false'})
    fname = StringField(u'Firstname <span class="star">*</span>',
                        validators=[validators.DataRequired(), validators.length(max=20)],
                        render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    lname = StringField(u'Lastname <span class="star">*</span>',
                        validators=[validators.DataRequired(), validators.length(max=20)],
                        render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    institute = StringField(u'Institute <span class="star">*</span>',
                            validators=[validators.DataRequired(), validators.length(max=50)],
                            render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    country = SelectField(u'Country <span class="star">*</span>', validators=[validators.DataRequired()],
                          choices=country_list, render_kw={'data-native-menu': 'false'})
    email1 = EmailField(u'Email <span class="star">*</span>',
                        validators=[validators.DataRequired(), validators.Email(), validators.EqualTo('email2')],
                        render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    email2 = EmailField(u'Confirm Email <span class="star">*</span>',
                        validators=[validators.DataRequired(), validators.Email()],
                        render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    pword1 = PasswordField(u'Enter password <span class="star">*</span>', validators=[validators.DataRequired(),
                                                                                      validators.EqualTo('pword2',
                                                                                                         message="Passwords must be equal")],
                           render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    pword2 = PasswordField(u'Confirm password <span class="star">*</span>', validators=[validators.DataRequired()],
                           render_kw={'data-clear-btn': 'true', 'placeholder': '...'})


class UploadForm(RedirectForm):
    case_num = StringField(u'Patient case number', validators=[validators.DataRequired(), validators.length(max=50)],
                           render_kw={'data-clear-btn': 'true', 'placeholder':'...'})
    consultant = StringField(u'Consultant', validators=[validators.DataRequired(), validators.length(max=50)],
                             render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    clinic_details = TextAreaField(u'Clinical details', validators=[validators.DataRequired()],
                                   render_kw={'data-clear-btn': 'true', 'placeholder': '...', 'rows': 5})
    prov_diag = StringField(u'Provisional diagnosis', validators=[validators.DataRequired()],
                            render_kw={'data=clear-btn': 'true', 'placeholder': '...'})
    name = StringField(u'Slide name', validators=[validators.DataRequired(), validators.length(max=50)],
                       render_kw={'data-clear-btn': 'true', 'placeholder': '...'})
    type = SelectField(u'Cancer type', choices=[('oral', 'Oral'), ('stomach', 'Stomach'), ('chest', 'Chest')],
                       validators=[validators.DataRequired()], render_kw={'data-native-menu': 'false'})
    u_file = FileField(u'File', render_kw={'data-role': 'none'})
