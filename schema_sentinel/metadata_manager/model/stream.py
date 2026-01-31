import json

import sqlalchemy as db
from sqlalchemy import ForeignKey, select

from . import CommonBase


class Stream(CommonBase):
    __tablename__ = "streams"
    stream_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    stream_name = db.Column(db.String)
    stream_owner = db.Column(db.String)
    comment = db.Column(db.String)
    table_name = db.Column(db.String)
    source_type = db.Column(db.String)
    base_tables = db.Column(db.String)
    type = db.Column(db.String)
    stale = db.Column(db.String)
    mode = db.Column(db.String)
    stale_after = db.Column(db.String)
    invalid_reason = db.Column(db.String)
    owner_role_type = db.Column(db.String)
    created = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Stream).filter_by(stream_id=self.stream_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["stream_name"] = self.stream_name
        return json.dumps(id)
