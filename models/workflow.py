from extras_mongoengine.fields import StringEnumField
from mongoengine import Document, fields

from models.workflow_status import WorkflowStatus
from models.step import Step
from models.step_status import StepStatus
from models.user import User


class Workflow(Document):
    meta = {
        'indexes': [
            'owner',
        ],
    }

    owner = fields.ReferenceField(User, require=True)
    name = fields.StringField(required=True)
    status = StringEnumField(WorkflowStatus, require=True,
                             default=WorkflowStatus.IN_PROGRESS)

    def get_steps_by_status(self, status):
        return Step.objects(owner=self.owner,
                            status=status)

    @property
    def steps(self):
        steps = {}
        for status in StepStatus:
            steps[status.name] = self.get_steps_by_status(status)
        return steps
