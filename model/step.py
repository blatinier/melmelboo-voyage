from mongokit import Document


class Step(Document):
    structure = {
        'name': unicode,
        'description': unicode,
        'key': unicode,
        'is_blocked_by': list,
    }

    validators = {
        'name': lambda x: len(x) > 0,
    }

    default_values = {
    }

    use_dot_notation = True

    indexes = [
        {'fields': ['name']},
    ]
