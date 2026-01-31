import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Pipe(CommonBase):
    __tablename__ = "pipes"
    pipe_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))

    pipe_name = db.Column(db.String, primary_key=True)
    pipe_owner = db.Column(db.String)
    pipe_definition = db.Column(db.String)
    is_autoingest_enabled = db.Column(db.String)
    notification_channel_name = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    pattern = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Pipe).filter_by(pipe_id=self.pipe_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["pipe_name"] = self.pipe_name_name
        return json.dumps(id)
