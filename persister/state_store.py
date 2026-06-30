import pandas as pd, pathlib as pl, logging, sqlalchemy
from sqlalchemy.exc import OperationalError, DatabaseError
from constant import constants as cons

logger = logging.getLogger(__name__)

class StateStore():
    """Class that handles file operations for orchestrator class for caching and remembering previous sessions."""
    def __init__(self, table_name, engine, user_id):
        """Store properties and set configuration parsing."""
        self.table_name=table_name
        self.engine=engine
        self.user_id=user_id
        self.data=None

    def manage_files(self):
        """Load and clear duplicates from all saved files."""
        self._load_memory()
        self._clear_memory_dupli()

    def _clear_memory_dupli(self):
        """Drop duplicates from all loaded files."""
        self.data=self.data.drop_duplicates()

    def _load_memory(self):
        """Load all files or reset it to fallback."""
        db_count=self._count_query_db(self.table_name)
        file=self.load_file(db_count)
        if not isinstance(file, pd.DataFrame):
            self.data=pd.DataFrame(columns=cons.TABLE_COLUMNS_PREVIOUS)
        else:
            self.data=file
        return True

    def concat_file(self, df:pd.DataFrame):
        """Concat dataframes for expanding files given in state.json.

        Args:
            df: df that  to their update.
            """
        self.data=pd.concat(objs=[self.data, df], ignore_index=True)
        return self

    def save_file(self):
        """Save file to db."""
        self.data[cons.TABLE_ID_USERS]=self.user_id
        self.data.to_sql(self.table_name, self.engine, if_exists='append', index=False)
        return self

    def _count_query_db(self, table_name):
        # grab row 0 col 0, warning is for iterator type, without chunk size arg read_SQL only returns df
        try:
            count = pd.read_sql(sqlalchemy.text(f'SELECT COUNT(*) FROM "{table_name}"'), self.engine).iloc[0, 0]  # noqa
        except (DatabaseError, pd.errors.DatabaseError):
            count = 0
        return count

    def load_file(self, db_count=0):
        """Load file from internal config path."""
        if db_count != 0:self.data=pd.read_sql(sqlalchemy.text(f'SELECT * FROM "{cons.TABLE_NAME_PREVIOUS_DATA}" WHERE {cons.TABLE_ID_USERS}=:user_id'), self.engine, params={cons.TABLE_ID_USERS: self.user_id})
        else: #db error and empty db table
            logger.info(f"Value not found at {cons.TABLE_NAME_PREVIOUS_DATA}")
            return None
        return self.data
