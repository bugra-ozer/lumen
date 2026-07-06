import sqlalchemy, logging, constant.constants as cons
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, NoResultFound
from db.models import User, RefreshToken

logger = logging.getLogger(__name__)

class SessionManager():
    def __init__(self, db:SQLAlchemy):
        self.db = db

    def write_user(self, username, role, pw_hash):
        """Given username, role, pw_hash, writes user to database."""
        try:
            self.db.session.add(User(username=username, role=role, pw_hash=pw_hash))
            self.db.session.commit()
            return True
        except IntegrityError:
            self.db.session.rollback()
            logger.error(cons.TABLE_ERROR_INTEGRITY)
            return False

    def read_username(self, username):
        """Checks if username exists, return User object or False if not."""
        try:return self.db.session.query(User).filter(User.username==username).one()
        except NoResultFound:
            return False

    def read_user_id(self, user_id):
        """Checks if user_id exists, return User object or False if not."""
        try:return self.db.session.query(User).filter(User.user_id==user_id).one()
        except NoResultFound:
            return False

    def read_ref_token(self, refresh_token):
        """Checks if refresh_token exists, return RefreshToken object or False if not."""
        try:return self.db.session.query(RefreshToken).filter(RefreshToken.refresh_token==refresh_token).one()
        except NoResultFound:
            return False

    def write_ref_token(self, refresh_token, user_id):
        """Given refresh_token, user_id, writes RefreshToken to database."""
        try:
            self.db.session.add(RefreshToken(refresh_token=refresh_token, user_id=user_id))
            self.db.session.commit()
            return True
        except IntegrityError:
            self.db.session.rollback()
            return False

    def delete_ref_token(self, refresh_token):
        """Deletes given refresh_token from database."""
        to_delete=self.read_ref_token(refresh_token)
        if to_delete:
            self.db.session.delete(to_delete)
            self.db.session.commit()

    def delete_all_ref_tokens(self, user_id):
        """Deletes all refresh_tokens from database given user_id."""
        to_delete = self.read_user_id(user_id)
        if to_delete:
            self.db.session.query(RefreshToken).filter(RefreshToken.user_id==user_id).delete()
            self.db.session.commit()