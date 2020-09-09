from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class basicform(FlaskForm):
    entree = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


def formbuilder(description):
    "construit un formulaire web a partir d'une description"
    fieldfunctions = {
        "B": "BooleanField",
        "DS": "DateField",
        "D": "DateTimeField",
        "N": "DecimalField",
        "FF": "FileField",
        "F": "FloatField",
        "K": "HiddenField",
        "E": "IntegerField",
        "L": "Label",
        "FFS": "MultipleFileField",
        "P": "PasswordField",
        "R": "RadioField",
        "S": "SelectField",
        "SS": "SelectMultipleField",
        "T": "StringField",
        "OK": "SubmitField",
    }

    class dynform(FlaskForm):
        pass
