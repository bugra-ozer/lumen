#Pandas operation constants
FILTER_VALUE='value'
FILTER_OPERATOR='operator'
FILTER_COLUMN='column'
IMDB_ID_COLUMN = 'IMDBid'
IMDB_ID_COLUMN_LEGACY = 'tconst'
GENRE_COLUMN = 'Genre'
GENRE_COLUMN_LEGACY = 'genres'
PUBLISHED_COLUMN = 'Published'
TITLE_TYPE_COLUMN = 'Title Type'
TITLE_TYPE_COLUMN_LEGACY = 'titleType'
PUBLISHED_COLUMN_LEGACY = 'startYear'
NUMBER_OF_VOTES_COLUMN = 'Number of Votes'
NUMBER_OF_VOTES_COLUMN_LEGACY = 'numVotes'
PRIMARY_TITLE_COLUMN = 'Primary Title'
PRIMARY_TITLE_COLUMN_LEGACY = 'primaryTitle'
AVERAGE_RATING_COLUMN = 'Average Rating'
BAYES_SCORE_COLUMN = 'Bay Score'
PATH_COLUMN='path'
DECAY_FACTOR_COLUMN = 'Decay Factor'
ADJUSTED_SCORE_COLUMN = 'Adjusted Score'
DATE_COLUMN = 'Date'
GENRE_LIST=["action", "adventure", "animation", "biography", "comedy", "crime", "documentary", "drama", "family", "fantasy", "film-noir", "game-show", "history", "horror", "music", "musical", "mystery", "news", "reality-tv", "romance", "sci-fi", "short", "sport", "talk-show", "thriller", "war", "western"]
COLUMNS_TO_KEEP='IMDBid', 'Average Rating', 'Number of Votes', 'Primary Title', 'Published', 'Genre'
COLUMNS_TO_KEEP_LEGACY='tconst', 'averageRating', 'numVotes', 'primaryTitle', 'startYear', 'genres'
COLUMN_RENAME_DICT={'tconst': 'IMDBid','averageRating': 'Average Rating',
                                    'numVotes': 'Number of Votes','titleType': 'Title Type',
                                    'primaryTitle': 'Primary Title','originalTitle': 'Original Title','isAdult': 'Is Adult',
                                    'startYear': 'Published','endYear': 'End Year','runtimeMinutes': 'Run Time Minutes','genres': 'Genre'}

#Pandas errors
ERROR_APPLY_CON='Failed to apply condition to the file.'
ERROR_LOAD_BASE_DATA='Failed to load base data'
ERROR_LOAD_TSV_PATH='Failed to load tsv paths'
ERROR_WRONG_FILTER_OR_DF='Failed to load filter_tools or DataFrame'

#CLI
INFO_PRESS_ANY='Press any key to continue...'
INFO_LOAD_BASE_DATA='loading base data file...'
INFO_MERGE_TSV='merging tsv file(s)...'
INFO_LOAD_DONE='load complete!'

#Config cons
PREVIOUS_DATA_KEY = 'previous_data'
BAYESIAN_DATA_KEY = 'bayesian_data'
FALLBACK_KEY = 'fallback'
PATH_KEY = 'path'
BASE_DATA_EXP_FILE = 'base_data_exp.json'
CONFIG_DIR = 'config'
BASE_DATA_EXP_JSON='last_update'

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

#Bayes cons
M_POOL=25
N_POP=5

#DB cons
USERS_TABLE_NAME= 'USERS'
USER_DEFAULT_ROLE='BASIC'