import pandas as pd, pathlib as pl, logging, sqlalchemy
from sqlalchemy.exc import OperationalError, DatabaseError
from constant import constants as cons

logger = logging.getLogger(__name__)

class StateStore():
    """Class that handles file operations for orchestrator class for caching and remembering previous sessions."""
    def __init__(self, table_name, engine):
        """Store properties and set configuration parsing."""
        self.table_name=table_name
        self.engine=engine
        self.previous_data=None

    def load_all_files(self):
        """Load and clear duplicates from all saved files."""
        self._load_memory()
        self._clear_memory_dupli()

    def _clear_memory_dupli(self):
        """Drop duplicates from all loaded files."""
        self.previous_data=self.previous_data.drop_duplicates()

    def _load_memory(self):
        """Load all files or reset it to given fallback property in config file."""
        file=self._load_file()
        if not isinstance(file, pd.DataFrame):
            self.previous_data=pd.DataFrame(columns=cons.PREVIOUS_COLUMNS)
        else:
            self.previous_data=file
        return True

    def concat_file(self, df:pd.DataFrame):
        """Concat dataframes for expanding files given in state.json.

        Args:
            df: df that  to their update.
            """
        self.previous_data=pd.concat(objs=[self.previous_data, df], ignore_index=True)
        return self

    def save_file(self):
        """Save file to internal config path."""
        missing_rows=self.previous_data[cons.TABLE_ID_PREVIOUS_DATA].isna()
        self.previous_data[missing_rows].to_sql(self.table_name, self.engine, if_exists='append', index=False)
        return self

    def _load_file(self):
        """Load file from internal config path."""
        try:
            self.previous_data=pd.read_sql(sqlalchemy.text(f'SELECT * FROM {cons.TABLE_NAME_PREVIOUS_DATA}'), self.engine)
        except (DatabaseError, pd.errors.DatabaseError):
            logger.exception(f"Value not found at {cons.TABLE_NAME_PREVIOUS_DATA}")
            raise Exception(f"Value not found at {cons.TABLE_NAME_PREVIOUS_DATA}")
        return self.previous_data
