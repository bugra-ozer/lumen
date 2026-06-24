from validator import validator
from os import access
from flask import request, Flask, jsonify
from main import AppService
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from constant import constants as cons
from constant import constants_dev as cons_dev
from db.database import db, engine_standalone, DATABASE_URL
from db.models import *
from persister.session_manager import SessionManager
import secrets, bcrypt, jwt, os, logging, sqlalchemy

logger = logging.getLogger(__name__)

os.chdir(Path(__file__).parent.parent)
load_dotenv()
secret_key=os.environ.get("SECRET_KEY")
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app_service=AppService(engine_standalone)
session_manager = SessionManager(db)
PUBLIC_PATHS=cons.PUBLIC_PATHS

@app.before_request
def before_request():
    """Authorization check before hitting endpoints of API."""
    if request.path not in PUBLIC_PATHS: #JWT check, request not hitting login or refresh endpoints
        token=request.headers.get(cons.AUTHORIZATION) #Entire authz token with 'Bearer' in it
        if token is None:
            return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_MISSING}), 401
        else:
            token=token.split(' ')
            if len(token)<2: return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_INVALID}), 401
            else: token=token[1]
            try: jwt.decode(token, secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError: return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_EXPIRED}), 401
            except jwt.InvalidTokenError: return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_INVALID}), 401
    return None

@app.route('/login', methods=["POST"])
def login():
    """Hashed credentials verification."""
    text=request.get_json(force=True)
    username=text.get('username')
    pw=text.get("pw")
    pw=pw.encode('UTF-8')
    user_object=session_manager.read_username(username)
    if not user_object:
        bcrypt.checkpw(pw, cons_dev.DUMMY_HASHED_PW) # noqa. For hitting same average time on fail cases
        return jsonify({'status': cons.ERROR, 'message': cons.INVALID_CREDENTIALS}), 401
    else:
        if bcrypt.checkpw(pw, user_object.pw_hash):
            ref_token=secrets.token_hex(32)
            session_manager.write_ref_token(ref_token, user_object.user_id)
            access_token=jwt.encode(payload={'id': user_object.user_id, 'exp': datetime.now(timezone.utc)+timedelta(minutes=15), 'role': user_object.role}, key=secret_key, algorithm='HS256')
            return jsonify({'access_token': access_token, 'refresh_token': ref_token, 'id': user_object.user_id}), 200
        else:
            return jsonify({'status': cons.ERROR, 'message': cons.INVALID_CREDENTIALS}), 401

@app.route("/refresh", methods=['POST'])
def refresh():
    """Acquire new access token endpoint."""
    text=request.get_json(force=True)
    token=text.get('refresh_token')
    ref_token_object=session_manager.read_ref_token(token)
    if ref_token_object:
        user_id=ref_token_object.user_id
        if ref_token_object.expiry_at<=datetime.now(timezone.utc):
            return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_EXPIRED}), 401
        else:
            user_object=session_manager.read_user_id(user_id)
            access_token=jwt.encode(payload={'id': user_id, 'exp': datetime.now(timezone.utc)+timedelta(minutes=15), 'role': user_object.role}, key=secret_key, algorithm='HS256')
            return jsonify({'access_token': access_token, 'refresh_token': token})
    else:
        return jsonify({'status': cons.ERROR, 'message': cons.TOKEN_INVALID}), 401

@app.route("/recommendations", methods=['POST'])
def service():
    """End to end service endpoint."""
    text = request.get_json(force=True)
    filter_tools = text.get('filter_tools')
    if not validator.is_valid_filter_tools(filter_tools):
        return jsonify({'status': cons.ERROR, 'message': cons.FILTER_TOOLS_INVALID})
    response=app_service.run(filter_tools)
    response=jsonify(response)
    return response

@app.route("/health", methods=['GET'])
def health():
    """Simple health endpoint."""
    return jsonify({'status': cons.OK})

def db_setup(api_app, main_app_service):
    db.init_app(api_app)
    with api_app.app_context():
        db.create_all()
        db_seed(main_app_service)

def db_seed(main_app_service):
    existing_imdb_ids = [row.imdb_id for row in db.session.query(Content.imdb_id).all()]
    is_in_mask = ~main_app_service.data[cons.IMDB_ID_COLUMN].isin(existing_imdb_ids)
    minimal_df = main_app_service.data[is_in_mask]
    try:
        minimal_df = minimal_df.drop(
            columns=[cons.DECAY_FACTOR_COLUMN, cons.BAYES_SCORE_COLUMN, cons.DATE_COLUMN, cons.ADJUSTED_SCORE_COLUMN])
    except ValueError:
        logger.error(ValueError)
    if not len(minimal_df) == 0:
        minimal_df.to_sql((f'{cons.TABLE_NAME_CONTENT}'), if_exists='append', index=False, con=db.engine)

db_setup(app, app_service)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)