from flask_wtf import FlaskForm
import wtforms as F
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import Select, html_params
from itertools import chain


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class BasicForm(FlaskForm):
    entree = F.MultipleFileField("entree", validators=[DataRequired()])
    sortie = F.StringField("sortie", validators=[DataRequired()])
    submit = SubmitField("executer")


class Dynmultiselect(Select):
    """genere le code html pour une liste dynamique avec VueJS"""

    pass


def select_multi_checkbox(field, ul_class="", **kwargs):
    kwargs.setdefault("type", "checkbox")
    field_id = kwargs.pop("id", field.id)
    html = [u"<ul %s>" % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u"%s-%s" % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options["checked"] = "checked"
        html.append(u"<li><input %s /> " % html_params(**options))
        html.append(u'<label for="%s">%s</label></li>' % (field_id, label))
    html.append(u"</ul>")
    return u"".join(html)


class DynSelectfieldwidget(F.SelectMultipleField):
    """restitue un champ multiple dynamique avec vueJs"""

    def __init__(self, vmodel=None):
        super(MyTextInput, self).__init__()


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
    variables = description.get("variables", dict())
    params = description.get("parametres", dict())
    # print("recup description", description)
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

        if not description.get("no_in"):
            setattr(CustomForm, "entree", F.MultipleFileField("entree"))
            varlist.append(("entree", "entree"))
        if description["__mode__"] == "api":
            setattr(CustomForm, "x_ws", F.BooleanField("x_ws"))
            varlist.append(("x_ws", "voir resultat en mode webservice"))
        else:
            setattr(CustomForm, "sortie", F.StringField("sortie"))
            varlist.append(("sortie", "sortie"))
    print("formbuilder: variables", list(chain(params.items(), variables.items())))
    for name, definition in chain(params.items(), variables.items()):

        nom, typevar = name.split("(", 1) if "(" in name else (name, "T)")
        typevar = typevar[:-1]
        vlist = []
        if ":" in typevar:
            tmp2 = typevar.split(":")
            typevar = tmp2[0]
            vlist = tmp2[1:]
        if vlist and typevar:
            setattr(
                CustomForm, nom, fieldfunctions.get(typevar)(definition, choices=vlist)
            )
        else:
            setattr(
                CustomForm, nom, fieldfunctions.get(typevar, F.StringField)(definition)
            )
        varlist.append((nom, definition))

    if description["__mode__"] == "api":
        setattr(
            CustomForm,
            "x_ws",
            F.BooleanField("voir resultats en mode webservice"),
        )

    setattr(CustomForm, "submit", SubmitField("executer"))
    # print("cree customform", varlist)
    return CustomForm, varlist
