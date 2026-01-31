import json

import sqlalchemy as db
from sqlalchemy import select, ForeignKey

from . import CommonBase


class Table(CommonBase):
    __tablename__ = "tables"
    table_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    table_name = db.Column(db.String)

    table_owner = db.Column(db.String)
    table_type = db.Column(db.String, default="TABLE")
    is_transient = db.Column(db.String, default="N")
    clustering_key = db.Column(db.String)
    comment = db.Column(db.String)
    row_count = db.Column(db.Integer)
    bytes = db.Column(db.Integer)
    retention_time = db.Column(db.Integer)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    last_ddl = db.Column(db.String)
    last_ddl_by = db.Column(db.String)
    auto_clustering_on = db.Column(db.String, default="OFF")
    change_tracking = db.Column(db.String, default="OFF")
    is_external = db.Column(db.String, default="N")
    enable_schema_evolution = db.Column(db.String, default="N")
    owner_role_type = db.Column(db.String)
    is_event = db.Column(db.String, default="N")

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Table).filter_by(table_id=self.table_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["table_name"] = self.table_name
        return json.dumps(id)