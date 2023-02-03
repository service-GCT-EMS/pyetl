from flask_wtf import FlaskForm
import wtforms as F
from wtforms import StringField, PasswordField, BooleanField, SubmitField, widgets
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


class Dynselect(Select):
    """genere le code html pour une liste dynamique avec VueJS"""

    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        html = ["<select %s>" % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append("</select>")
        return Markup("".join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            # Handle the special case of a 'True' value.
            value = text_type(value)

        options = dict(kwargs, value=value)
        if selected:
            options["selected"] = True
        return Markup(
            "<option %s>%s</option>" % (html_params(**options), escape(label))
        )

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

    def __init__(self, definition, vmodel=None, **kwargs):
        cdef = kwargs.get("choices")  # choix dynamiques
        kwargs["choices"] = ""
        super(F.SelectMultipleField, self).__init__(**kwargs)


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
        "DS": DynSelectfieldwidget,
        "SS": F.SelectMultipleField,
        "DSS": DynSelectfieldwidget,
        "T": F.StringField,
        "OK": F.SubmitField,
    }
    variables = description.get("variables", dict())
    params = description.get("parametres", dict())
    print("recup description", description)
    varlist = []
    def_es = description.get("e_s", ())
    if description["__mode__"] == "api":
        setattr(CustomForm, "x_ws", F.BooleanField("x_ws"))
        varlist.append(("x_ws", "voir resultat en mode webservice"))
    if def_es:
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

        if description["__mode__"] != "api":
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
        if vlist and vlist[0].startswith("@") and not typevar.startswith("D"):
            typevar = "D" + typevar
            #on tagge l attribut en dynamique
        if vlist and typevar:
            setattr(
                CustomForm, nom, fieldfunctions.get(typevar)(definition, choices=vlist)
            )
        else:
            setattr(
                CustomForm, nom, fieldfunctions.get(typevar, F.StringField)(definition)
            )
        varlist.append((nom, definition))

    setattr(CustomForm, "submit", SubmitField("executer"))
    # print("cree customform", varlist)
    return CustomForm, varlist
