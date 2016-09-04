from sqlalchemy.ext.declarative import declared_attr

from gsweb import db


class User(db.Model):
    __tablename__ = 'users'

    @declared_attr
    def __table_args__(cls):
        return db.Index(None, db.func.lower(cls.name), unique=True, postgresql_where=db.text('NOT is_deleted')),

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    name = db.Column(db.String, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        deleted = ', is_deleted=True' if self.is_deleted else ''
        return '<User({}, account_id={}{})>'.format(self.id, self.account_id, deleted)
