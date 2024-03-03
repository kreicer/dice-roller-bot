from yoyo import read_migrations
from yoyo import get_backend

backend_server = get_backend('sqlite:///databases/server.db')
migrations_server = read_migrations('migrations/server')

with backend_server.lock():
    backend_server.apply_migrations(backend_server.to_apply(migrations_server))

backend_user = get_backend('sqlite:///databases/user.db')
migrations_user = read_migrations('migrations/user')

with backend_user.lock():
    backend_user.apply_migrations(backend_user.to_apply(migrations_user))
