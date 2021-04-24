from yoyo import get_backend
from yoyo import read_migrations


def migration():
    backend = get_backend('postgres://postgres:password@localhost/budget_bot')
    migrations = read_migrations('./migrations')

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
