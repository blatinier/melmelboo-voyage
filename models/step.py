from extras_mongoengine.fields import StringEnumField
from mongoengine import Document, fields

from models.step_status import StepStatus
from models.user import User


# TODO field validation
# TODO init db fixture for simple WF
class Step(Document):
    meta = {
        'indexes': [
            ('owner', 'status'),
            ('owner', 'key'),
        ],
    }

    owner = fields.ReferenceField(User, required=True)
    name = fields.StringField(require=True)
    description = fields.StringField(require=True)
    key = fields.StringField(require=True)
    status = StringEnumField(StepStatus, require=True,
                             default=StepStatus.UNDECIDED)

    # List of step keys blocking this one
    is_blocked_by = fields.ListField(fields.StringField)
    # List of plugins linked to this task
    plugins = fields.ListField(fields.StringField)
    user_answer = fields.DictField()
