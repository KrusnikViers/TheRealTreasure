from alembic import context

from app.database.base_model import Base
from app.database.migrations import router

# This forces all models to be defined, and therefore to be added in the Base model metadata.
from app.models.all import *

target_metadata = Base.metadata
with router.MigrationScope.current_engine().connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
