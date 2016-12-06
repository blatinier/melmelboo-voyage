from flask_wtf.form import Form
from wtforms import TextField, TextAreaField, SubmitField, validators


class ContactForm(Form):
    name = TextField("Name", [validators.Required("Renseignez votre nom")])
    email = TextField("Email", [validators.Required("Renseignez votre email"),
                                validators.Email("Mettez un email valide")])
    website = TextField("Website")
    lil_word = "Ecrivez-nous un petit mot :)"
    message = TextAreaField("Message",
                            [validators.Required(lil_word)])
    submit = SubmitField("Envoyer !")
