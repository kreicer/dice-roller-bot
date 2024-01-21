from yoyo import read_migrations
from yoyo import get_backend

backend = get_backend('sqlite:///databases/server.db')
migrations = read_migrations('migrations/server')

with backend.lock():

    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))
