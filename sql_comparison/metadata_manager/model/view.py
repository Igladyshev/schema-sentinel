import json

import sqlalchemy as db
from sqlalchemy import select, ForeignKey

from . import CommonBase


class View(CommonBase):
    __tablename__ = "views"
    view_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    view_name = db.Column(db.String)
    view_owner = db.Column(db.String)
    view_definition = db.Column(db.String)
    is_secure = db.Column(db.String)
    is_materialized = db.Column(db.String)
    change_tracking = db.Column(db.String)
    created = db.Column(db.String)
    enable_schema_evolution = db.Column(db.String)
    owner_role_type = db.Column(db.String)
    comment = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(View).filter_by(view_id=self.view_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["view_name"] = self.view_name
        return json.dumps(id)