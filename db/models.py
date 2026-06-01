from db.database import db
from constant import constants as cons
from datetime import datetime, timezone

class User(db.Model):
    __tablename__=cons.USERS_TABLE_NAME
    user_id=db.Column('user_id',db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    role=db.Column(db.String(80),nullable=False,default=cons.USER_DEFAULT_ROLE)
    password_hash=db.Column(db.String(60),nullable=False)

#ADD CONTENT AND HISTORY TABLES
