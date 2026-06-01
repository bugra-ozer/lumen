from db.database import db
from constant import constants as cons
from datetime import datetime, timezone, timedelta

class User(db.Model):
    __tablename__=cons.TABLE_NAME_USERS
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    role=db.Column(db.String(80),nullable=False,default=cons.USER_DEFAULT_ROLE)
    password_hash=db.Column(db.String(60),nullable=False)

class Content(db.Model):
    __tablename__=cons.TABLE_NAME_CONTENT
    imdb_id=db.Column(db.String(80),primary_key=True)
    average_rating=db.Column(db.Float,nullable=False)
    num_votes=db.Column(db.Integer,nullable=False)
    title_type=db.Column(db.String(80),nullable=True)
    primary_title=db.Column(db.String(160),nullable=False)
    start_year=db.Column(db.Integer,nullable=False)
    genres=db.Column(db.String(80),nullable=False)

class RefreshToken(db.Model):
    __tablename__=cons.TABLE_NAME_REFRESH_TOKEN
    refresh_token_id=db.Column(db.Integer,primary_key=True)
    refresh_token=db.Column(db.String(64))
    user_id=db.Column(db.Integer,db.ForeignKey(f'{cons.TABLE_NAME_USERS}.user_id'))
    expiry_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc)+timedelta(days=30))

class PreviousData(db.Model):
    __tablename__=cons.TABLE_NAME_PREVIOUS_DATA
    previous_data_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey(f'{cons.TABLE_NAME_USERS}.user_id'))
    imdb_id=db.Column(db.String(80),db.ForeignKey(f'{cons.TABLE_NAME_CONTENT}.imdb_id'))
    date=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))

#ADD CONTENT AND HISTORY TABLES
