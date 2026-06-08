import pandas as pd
from constant import constants

def is_input_float(user_input):
    try:
        float(user_input)
        return True
    except ValueError: return False

def is_list_genre(genres:list):
    if all(is_input_genre(genre) for genre in genres):
        return True
    return False

def is_input_genre(user_input):
    if user_input.lower().strip() in constants.GENRE_LIST:
        return True
    return False

def is_ready_structure(df=None, filter_tools:dict=None):
    if is_valid_dataframe(df) and is_valid_filter_tools(filter_tools):
        return True
    return False

def is_valid_filter_tools(filter_tools):
    if filter_tools == {} or filter_tools is None: return True
    elif not isinstance(filter_tools, dict):
        return False
    else:
        for key, inner_dict in filter_tools.items():
            if not isinstance(inner_dict, dict):
                return False
    return True

def is_valid_dataframe(df:pd.DataFrame):
    if not isinstance(df, pd.DataFrame):
        return False
    for col in constants.CONTENT_COLUMNS_TO_KEEP:
        if col not in df.columns:
            return False
    return True
