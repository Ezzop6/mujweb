from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())
debug = os.environ.get("DEBUG")
if debug == "True": debug = True
else: debug = False

if debug:
    from database import DbUsersMain
else:
    from api.database import DbUsersMain
    
db = DbUsersMain()




from flask_wtf import FlaskForm
from wtforms import  TextAreaField, IntegerField, SelectField ,widgets, StringField, PasswordField, SubmitField, DateField, validators,ValidationError



import datetime

forbidden_words = ["admin","root","administrator"] # forbidden words in name, surname and login
forrbiden_letters = "!@#$%^&*()_+{}|:<>?/.,;'[]\=-`~"

class CustomTest:
    @staticmethod
    def contains_forbidden_letters(data):
        if len(data) == 0:
            return
        for letter in data:
            if letter in forrbiden_letters:
                return True
            
    @staticmethod        
    def contains_digit(data):
        if len(data) == 0:
            return
        for letter in data:
            if letter.isdigit():
                return True
            
    @staticmethod
    def validate_password(password, password2):
        password = password.data
        special_characters = "!@#$%^&*()_+|:<>?[]\;',./`~ěščřžýáíéúůťďňóĚŠČŘŽÝÁÍÉÚŮŤĎŇÓ"
        min_length = 8
        digit = sum(1 for letter in password if letter.isdigit())
        special = sum(1 for letter in password if letter in special_characters)
        small_letter = sum(1 for letter in password if letter.islower())
        big_letter = sum(1 for letter in password if letter.isupper())
        
        if min_length > len(password):
            raise ValidationError(f"Heslo musí mít minimálně {min_length} znaků")
        elif digit == 0:
            raise ValidationError("Heslo musí obsahovat alespoň jedno číslo")
        elif special == 0:
            raise ValidationError("Heslo musí obsahovat alespoň jeden speciální znak")
        elif small_letter == 0:
            raise ValidationError("Heslo musí obsahovat alespoň jedno malé písmeno")
        elif big_letter == 0:
            raise ValidationError("Heslo musí obsahovat alespoň jedno velké písmeno")
        elif password != password2:
            raise ValidationError("Hesla se neshodují")
        
    @staticmethod
    def validate_name(name):
        name = name.data
        if len(name) == 0:
            return
        if len(name) < 2:
            raise ValidationError(f"Jméno musí mít alespoň 2 znaky: {name}")
        if name in forbidden_words:
            raise ValidationError(f"nesmíš použít toto jméno: {name}")
        if CustomTest.contains_forbidden_letters(name):
            raise ValidationError(f"nesmíš použít tyto znaky v jménu: {forrbiden_letters}")
        if CustomTest.contains_digit(name):
            raise ValidationError(f"nesmíš použít číslice v jménu: {name}")
        
    @staticmethod
    def validate_street_number(street_number):
        street_number = street_number.data
        if len(street_number) == 0:
            return
        if len(street_number) > 7:
            raise ValidationError(f"Číslo domu musí mít maximálně 6 znaků: {street_number}")
        for letter in street_number:
            if letter == "/": # asi to fakt zbytecne komplikuju
                continue
            if not letter.isdigit():
                raise ValidationError(f"Číslo domu musí být číslo: {street_number}")
        
            
    @staticmethod
    def validate_zip_code(zip_code):
        zip_code = zip_code.data
        if len (zip_code) == 0:
            return
        if len(zip_code) != 5:
            raise ValidationError(f"PSČ musí mít 5 číslic: {zip_code}")
        for letter in zip_code:
            if not letter.isdigit():
                raise ValidationError(f"PSČ musí být číslo: {zip_code}")
            
    @staticmethod
    def validate_street(street):
        street = street.data
        if len(street) == 0:
            return
        if len(street) < 2:
            raise ValidationError(f"Ulice musí mít alespoň 2 znaky: {street}")
        for letter in street:
            if letter.isdigit():
                raise ValidationError(f"Ulice nesmí obsahovat číslice: {street}")
        for letter in street:
            if letter in forrbiden_letters:
                raise ValidationError(f"Ulice nesmí obsahovat tyto znaky: {forrbiden_letters}")
            
    @staticmethod
    def validate_city(city):
        city = city.data
        if len(city) == 0:
            return
        if len(city) < 2:
            raise ValidationError(f"Město musí mít alespoň 2 znaky: {city}")
        for letter in city:
            if letter.isdigit():
                raise ValidationError(f"Město nesmí obsahovat číslice: {city}")
        for letter in city:
            if letter in forrbiden_letters:
                raise ValidationError(f"Město nesmí obsahovat tyto znaky: {forrbiden_letters}")
        
    
class LoginForm(FlaskForm):
    login = StringField('Login', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Heslo', [validators.Length(min=8, max=25), validators.DataRequired()])
    submit = SubmitField('Přihlásit se')
    
    def validate_login(self, login):
        login = login.data
        if not db.check_if_user_exists(login) == None:
            raise ValidationError(f"Login: {login} neexistuje")
        
    def validate_password(self, password):
        login = self.login.data
        password = password.data
        if not db.login_user(login, password):
            raise ValidationError("Špatné jméno nebo heslo")
    
class RegisterForm(FlaskForm):
    login = StringField('Login', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Heslo', [validators.Length(min=8, max=25), validators.DataRequired()])
    password2 = PasswordField('Heslo znovu', [validators.Length(min=8, max=25), validators.DataRequired()])
    submit = SubmitField('Registrovat se')
    
    
    def validate_login(self, login):
        login = login.data
        if login in forbidden_words:
            raise ValidationError(f"nesmíš použít tento login: {login}")
        if db.check_if_user_exists(login) == None:
            raise ValidationError(f"Uživatel s loginem {login} již existuje")
    
    def validate_password(self, password):
        CustomTest.validate_password(password, self.password2.data)