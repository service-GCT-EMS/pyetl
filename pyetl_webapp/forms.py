from flask_wtf import FlaskForm
import wtforms as F
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class BasicForm(FlaskForm):
    entree = F.MultipleFileField("entree", validators=[DataRequired()])
    sortie = F.FileField("sortie", validators=[DataRequired()])
    submit = SubmitField("executer")


def formbuilder(description):
    "construit un formulaire web a partir d'une description"

    class CustomForm(FlaskForm):
        pass

    fieldfunctions = {
        "B": F.BooleanField,
        "DS": F.DateField,
        "D": F.DateTimeField,
        "N": F.DecimalField,
        "FF": F.FileField,
        "F": F.FloatField,
        "K": F.HiddenField,
        "E": F.IntegerField,
        "L": F.Label,
        "FFS": F.MultipleFileField,
        "P": F.PasswordField,
        "R": F.RadioField,
        "S": F.SelectField,
        "SS": F.SelectMultipleField,
        "T": F.StringField,
        "OK": F.SubmitField,
    }
    variables = description.get("vars", ())
    varlist = []
    es = description.get("e_s", ())
    if es:
        def_es = es.split(";")
        if def_es[0]:
            setattr(
                CustomForm,
                "entree",
                F.MultipleFileField("entree", validators=[DataRequired()]),
            )
            varlist.append(("entree", def_es[0]))
        if def_es[1]:
            setattr(
                CustomForm, "sortie", F.FileField("sortie", validators=[DataRequired()])
            )
            varlist.append(("sortie", def_es[1]))

    else:
        setattr(CustomForm, "entree", F.MultipleFileField("entree"))
        setattr(CustomForm, "sortie", F.FileField("sortie"))
        varlist.append(("entree", "entree"))
        varlist.append(("sortie", "sortie"))

    for var in variables:
        name, definition = var.split("(", 1)

        setattr(CustomForm, name, StringField(name))
        varlist.append((name, name))

    setattr(CustomForm, "submit", SubmitField("executer"))
    print("cree customform", varlist)
    return CustomForm, varlist
