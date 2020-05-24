import logging

from flexiconf import Configuration
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.info import DEFAULT_DB_PATH
from app.database.migrations import router


class DatabaseConnection:
    def __init__(self, configuration: Configuration, for_tests: bool = False):
        url = self._generate_db_url(configuration, for_tests)
        logging.info("Database path is set to {}".format(url))
        self.engine = create_engine(url)
        self.make_session = sessionmaker(bind=self.engine)
        self.run_migrations()

    def run_migrations(self):
        logging.info('Running pending migrations')
        router.run_migrations(self.engine)

    @staticmethod
    def _generate_db_url(configuration: Configuration, for_tests: bool):
        if for_tests:
            return 'sqlite://'
        return "sqlite:///{}/storage.db".format(configuration.get_string('storage_directory', default=DEFAULT_DB_PATH))
