from flask_wtf.form import Form
from wtforms import TextField, TextAreaField, SubmitField, validators


class ContactForm(Form):
    name = TextField("Name", [validators.Required("Renseignez votre nom")])
    email = TextField("Email", [validators.Required("Renseignez votre email"), validators.Email("Mettez un email valide")])
    website = TextField("Website")
    message = TextAreaField("Message", [validators.Required("Ecrivez-nous un petit mot :)")])
    submit = SubmitField("Envoyer !")
