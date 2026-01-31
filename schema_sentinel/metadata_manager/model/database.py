import json
import sqlalchemy as db
from sqlalchemy import select
from . import CommonBase


class Database(CommonBase):
    __tablename__ = "databases"
    database_id = db.Column(db.String, primary_key=True)
    version = db.Column(db.String)
    environment = db.Column(db.String)
    database_name = db.Column(db.String)
    database_owner = db.Column(db.String)
    is_transient = db.Column(db.String, default="NO")
    comment = db.Column(db.String)
    created = db.Column(db.String)
    last_altered = db.Column(db.String)
    retention_time = db.Column(db.String)

    def save(self, session) -> None:

        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(Database).filter_by(
            database_id=self.database_id)

    def __get_id__(self) -> str:
        return json.dumps({
            "database_name": self.database_name,
            "version": self.version,
            "environment": self.environment
        })
        
    def __get_name__(self) -> str:
        return f"{self.database_name} v.{self.version}({self.environment})"
    