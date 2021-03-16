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
    sortie = F.StringField("sortie", validators=[DataRequired()])
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
    variables = description.get("variables", [])
    params = description.get("parametres", [])
    print("recup description", description)
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
        setattr(CustomForm, "sortie", F.StringField("sortie"))
        varlist.append(("entree", "entree"))
        varlist.append(("sortie", "sortie"))

    all_in = params + variables
    for var in all_in:
        name, definition = var.split("(", 1)
        definition = definition[-1]
        tmp = definition.split(",")
        ftyp = tmp[0]
        fname = tmp[1] if len(tmp) > 1 else name
        setattr(CustomForm, name, fieldfunctions.get(ftyp, F.StringField)(fname))
        varlist.append((name, name))

    setattr(CustomForm, "submit", SubmitField("executer"))
    print("cree customform", varlist)
    return CustomForm, varlist
