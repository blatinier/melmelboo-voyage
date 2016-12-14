from mongoengine import Document, fields


# TODO SSO (fb, google au moins, cf jarr)
# TODO field validation
class User(Document):
    meta = {
        'indexes': [
            'name',
            'email',
        ],
    }

    name = fields.StringField(required=True)
    email = fields.StringField(required=True)
