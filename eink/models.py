from . import db


class Task(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)
    task_id = db.Column(db.String(15),
                        index=True,
                        unique=True,
                        nullable=False)
    name = db.Column(db.Text)

    active = db.Column(db.Boolean)
    completed = db.Column(db.Boolean)
    containingProjectName = db.Column(db.Text)
    dueDate = db.Column(db.DateTime)
    estimatedMinutes = db.Column(db.Integer)
    flagged = db.Column(db.Boolean)
    inInbox = db.Column(db.Boolean)
    note = db.Column(db.Text)
    taskStatus = db.Column(db.String(15))

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'name': self.name,
            'active': self.active,
            'completed': self.completed,
            'containingProjectName': self.containingProjectName,
            'dueDate': self.dueDate.isoformat() if self.dueDate else None,
            'estimatedMinutes': self.estimatedMinutes,
            'flagged': self.flagged,
            'inInbox': self.inInbox,
            'note': self.note,
            'taskStatus': self.taskStatus,
        }
