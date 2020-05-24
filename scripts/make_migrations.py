from flexiconf import ArgsLoader, Configuration

from app.core.utils import global_logging_init
from app.database.connection import DatabaseConnection
from app.database.migrations import router

global_logging_init()

# Provide db_path command line parameter for this script.
# Make sure that:
# - directory app/database/migrations/versions exists
# - db_path directory exists as well
config = Configuration([ArgsLoader()])
connection = DatabaseConnection(config)

router.make_migrations(connection.engine)
