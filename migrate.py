from yoyo import read_migrations
from yoyo import get_backend

backend = get_backend('sqlite:///databases/test.db')
migrations = read_migrations('migrations')

with backend.lock():

    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))
