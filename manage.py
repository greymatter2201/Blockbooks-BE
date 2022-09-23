from flask.cli import FlaskGroup

from app import app, db
from flask_migrate import init, migrate, upgrade

cli = FlaskGroup(app)


@cli.command("update_db")
def create_db():
    migrate(directory='migrations')
    upgrade(directory='migrations')

@cli.command("create_db")
def create_db():
    init(directory='migrations')
    migrate(directory='migrations')
    upgrade(directory='migrations')

if __name__ == "__main__":
    cli()