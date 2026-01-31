import json
import sqlalchemy as db
from sqlalchemy import select, ForeignKey
from . import CommonBase


class ColumnConstraint(CommonBase):
    __tablename__ = "column_constraints"
    column_constraint_id = db.Column(db.String, primary_key=True)
    pk_constraint_id = db.Column(db.String, ForeignKey("constraints.constraint_id"))
    fk_constraint_id = db.Column(db.String, ForeignKey("constraints.constraint_id"))
    pk_column_id = db.Column(db.String, ForeignKey("columns.column_id"))
    fk_column_id = db.Column(db.String, ForeignKey("columns.column_id"))
    pk_name = db.Column(db.String)
    fk_name = db.Column(db.String)

    key_sequence = db.Column(db.String)
    comment = db.Column(db.String)
    created = db.Column(db.String)
    deferrability = db.Column(db.String)
    rely = db.Column(db.String)
    update_rule = db.Column(db.String)
    delete_rule = db.Column(db.String)

    def save(self, session) -> None:
        if not session.execute(self.exists()).first():
            session.add(self)
            session.commit()

    def exists(self) -> str:
        return select(ColumnConstraint).filter_by(column_constraint_id=self.column_constraint_id)

    def __get_id__(self) -> str:
        pk_column_id = json.loads(self.pk_column_id)
        fk_column_id = json.loads(self.fk_column_id)
        return json.dumps(
            {
                "pk_column_id": pk_column_id,
                "pk_name": self.pk_name,
                "fk_column_id": fk_column_id,
                "fk_name:": self.fk_name,
            }
        )
