import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Task(CommonBase):
    __tablename__ = "tasks"
    id = db.Column(db.String, primary_key=True)
    task_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    task_name = db.Column(db.String, primary_key=True)
    task_owner = db.Column(db.String)
    warehouse = db.Column(db.String)
    schedule = db.Column(db.String)
    predecessors = db.Column(db.String)
    state = db.Column(db.String)
    definition = db.Column(db.String)
    condition = db.Column(db.String)
    allow_overlapping_execution = db.Column(db.String)
    error_integration = db.Column(db.String)
    comment = db.Column(db.String)
    last_committed = db.Column(db.String)
    last_suspended = db.Column(db.String)
    owner_role_type = db.Column(db.String)
    config = db.Column(db.String)
    created = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Task).filter_by(id=self.id, task_id=self.task_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["task_name"] = self.task_name
        return json.dumps(id)
