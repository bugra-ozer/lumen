from flask_migrate import migrate
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
    number_of_votes=db.Column(db.Integer,nullable=False)
    primary_title=db.Column(db.String(160),nullable=False)
    published=db.Column(db.Integer,nullable=False)
    genre=db.Column(db.String(80),nullable=False)

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
    imdb_id=db.Column(db.String(80), db.ForeignKey(f'{cons.TABLE_NAME_CONTENT}.imdb_id'))
    date=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))