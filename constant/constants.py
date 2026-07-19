

#Pandas operation constants
FILTER_VALUE='value'
FILTER_OPERATOR='operator'
FILTER_COLUMN='column'
IMDB_ID_COLUMN = 'imdb_id'
IMDB_ID_COLUMN_LEGACY = 'tconst'
GENRE_COLUMN = 'genre'
GENRE_COLUMN_LEGACY = 'genres'
PUBLISHED_COLUMN = 'published'
TITLE_TYPE_COLUMN = 'title_type'
USER_ID_COLUMN = 'user_id'
TITLE_TYPE_COLUMN_LEGACY = 'titleType'
PUBLISHED_COLUMN_LEGACY = 'startYear'
NUMBER_OF_VOTES_COLUMN = 'number_of_votes'
NUMBER_OF_VOTES_COLUMN_LEGACY = 'numVotes'
PRIMARY_TITLE_COLUMN = 'primary_title'
PRIMARY_TITLE_COLUMN_LEGACY = 'primaryTitle'
AVERAGE_RATING_COLUMN = 'average_rating'
BAYES_SCORE_COLUMN = 'bay_score'
PATH_COLUMN='path'
DECAY_FACTOR_COLUMN = 'decay_factor'
ADJUSTED_SCORE_COLUMN = 'adjusted_score'
DATE_COLUMN = 'date'
USECOLS_COLUMN = 'usecols'
CHUNK_SIZE_TSV=150000
GENRE_LIST=["action", "adventure", "animation", "biography", "comedy", "crime", "documentary", "drama", "family", "fantasy", "film-noir", "game-show", "history", "horror", "music", "musical", "mystery", "news", "reality-tv", "romance", "sci-fi", "short", "sport", "talk-show", "thriller", "war", "western"]
CONTENT_COLUMNS_TO_KEEP= 'imdb_id', 'average_rating', 'number_of_votes', 'primary_title', 'published', 'genre'
CONTENT_COLUMNS_TO_KEEP_LEGACY= 'tconst', 'averageRating', 'numVotes', 'primaryTitle', 'startYear', 'genres'
TABLE_COLUMNS_PREVIOUS= 'previous_data_id', 'user_id', 'imdb_id', 'date'
COLUMN_RENAME_DICT={'tconst': 'imdb_id','averageRating': 'average_rating',
                                    'numVotes': 'number_of_votes','titleType': 'title_type',
                                    'primaryTitle': 'primary_title','originalTitle': 'original_title','isAdult': 'is_adult',
                                    'startYear': 'published','endYear': 'end_year','runtimeMinutes': 'run_time_minutes','genres': 'genre'}

#Pandas errors
ERROR_APPLY_CON='Failed to apply condition to the file.'
ERROR_LOAD_DB= 'Failed to load database'
ERROR_LOAD_TSV_PATH='Failed to load tsv paths'
ERROR_WRONG_FILTER_OR_DF='Failed to load filter_tools or DataFrame'
ERROR_SAVE='Failed to save file'
ERROR_COLUMN_NOT_FOUND='Column not found to rename:'
ERROR_PARSE_FILTER_TOOLS='Unable to parse filter tools'
ERROR_COLUMN_MASK='Column mask and mask are required to be both None or both valid.'

#CLI
INFO_PRESS_ANY='Press any key to continue...'
INFO_LOAD_DB= 'loading db...'
INFO_MERGE_TSV='merging tsv file(s)...'
INFO_LOAD_DONE='load complete!'

#Config cons
PREVIOUS_DATA_KEY = 'previous_data'
BAYESIAN_DATA_KEY = 'bayesian_data'
FALLBACK_KEY = 'fallback'
PATH_KEY = 'path'
DB_EXP_FILE = 'db_exp.json'
CONFIG_DIR = 'config'
DB_EXP_JSON= 'last_update'
STR_PARQUET='parquet'
STR_TSV='tsv'
STR_SQL='sql'
STR_JSON='json'
DATASET_JSON='dataset.json'
DATASET_FILENAME_KEY = 'filename'
DATASET_COLUMN_MASK_KEY = 'column_mask'
DATASET_MASK_KEY = 'mask'

#API cons
PUBLIC_PATHS='/login', '/refresh', '/health'
FILTER_TOOLS_INVALID='Invalid filter_tools'
FILTER_TOOLS_NOT_SURE='Filter tools not found or invalid'
ERROR=('ERROR')
TOKEN_EXPIRED='Token has expired'
TOKEN_INVALID='Token is invalid'
TOKEN_MISSING='Token is missing'
OK=('ok')
AUTHORIZATION='Authorization'
INVALID_CREDENTIALS='Invalid credentials'
REGISTER_FAILED='Registration failed'
LOGOUT_FAILED='Logout failed'
SERVER_FAILED='Server error, try again'
USER_DEFAULT_ROLE='BASIC'
PAYLOAD_USER_ID='user_id'
PAYLOAD_EXP='exp'
PAYLOAD_REFRESH_TOKEN='refresh_token'
PAYLOAD_ACCESS_TOKEN='access_token'
PAYLOAD_ERROR='error'
PAYLOAD_STATUS='status'
PAYLOAD_MESSAGE='message'
PAYLOAD_PW='pw'
PAYLOAD_USERNAME='username'
PAYLOAD_UTF8='UTF-8'
METHOD_GET='GET'
METHOD_POST='POST'
ENDPOINT_REFRESH="/refresh"
ENDPOINT_HEALTH="/health"
ENDPOINT_LOGIN="/login"
ENDPOINT_RECOMMENDATIONS="/recommendations"
ENDPOINT_REGISTER="/register"
ENDPOINT_LOGOUT="/logout"

#Bayes cons
M_POOL=25
N_POP=2

#DB cons
TABLE_NAME_USERS= 'USERS'
TABLE_NAME_CONTENT= 'CONTENT'
TABLE_NAME_GENRE= 'GENRE'
TABLE_NAME_REFRESH_TOKEN= 'REFRESH_TOKEN'
TABLE_NAME_PREVIOUS_DATA= 'PREVIOUS_DATA'
DEFAULT_NAME_DB_URL="DATABASE_URL"
FILE_NAME_DATABASE= 'lumen.db'
FOLDER_NAME_INSTANCE='instance'
ERROR_CONNECT_DB= 'Failed to connect to database'
TABLE_ID_PREVIOUS_DATA= 'previous_data_id'
TABLE_ID_USERS= 'user_id'
TABLE_ID_DATE= 'date'
TABLE_ERROR_INTEGRITY='Integrity error, duplicates found'
TABLE_ERROR_NOT_FOUND= 'Item not found'
USERS_LOCAL_USER= 'local_user'
COLUMN_USERNAME= 'username'
COLUMN_PW_HASH= 'pw_hash'
COLUMN_ROLE= 'role'
COLUMN_CREATED_AT= 'created_at'
PW_HASH_LOCAL_USER= b'local'
CONTENT_COLUMNS_LIST=[IMDB_ID_COLUMN, AVERAGE_RATING_COLUMN, NUMBER_OF_VOTES_COLUMN, PRIMARY_TITLE_COLUMN, PUBLISHED_COLUMN, GENRE_COLUMN]
TABLE_NAME_UPSERT_TEMP= 'UPSERT_TEMP'

#docker
ERROR_DOCKER_NOT_LAUNCHED="PostgreSQL is configured but unreachable. Start Docker first."

#os
FILE_NAME_ENV='.env'
FILE_NAME_NON_TITLE_TYPE= ['ratings']

#state store
DECAY_FACTOR_THRESHOLD=[10, 15, 20, 30, 45]
DECAY_FACTOR_THRESHOLD_DEFAULT=0.99915
DECAY_FACTOR_VALUES=[0.99965, 0.99955, 0.99945, 0.99935, 0.99925]