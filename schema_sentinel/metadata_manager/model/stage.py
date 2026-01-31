import json

import sqlalchemy as db
from sqlalchemy import select, ForeignKey

from . import CommonBase


class Stage(CommonBase):
    __tablename__ = "stages"
    stage_id = db.Column(db.String, primary_key=True)
    schema_id = db.Column(db.String, ForeignKey("schemas.schema_id"))
    stage_name = db.Column(db.String)
    stage_owner = db.Column(db.String)
    stage_url = db.Column(db.String)
    stage_region = db.Column(db.String)
    stage_type = db.Column(db.String, default="internal named")
    has_credentials = db.Column(db.String)
    has_encryption_key = db.Column(db.String)
    cloud = db.Column(db.String)
    notification_channel = db.Column(db.String)
    storage_integration = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Stage).filter_by(stage_id=self.stage_id)

    def __get_id__(self) -> str:
        id = json.loads(self.schema_id)
        id["stage_name"] = self.stage_name
        return json.dumps(id)
