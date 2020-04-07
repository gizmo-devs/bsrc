import psycopg2, psycopg2.extras

import click
from flask import current_app as app, g
from flask.cli import with_appcontext

import os.path

def get_db():
    try:
        con = psycopg2.connect(
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD']
        )
    except (Exception, psycopg2.DatabaseError) as error:
        print('There has been a problem connecting to the database:')
        print(error)
    return con


def query_db(query, args=(), one=False, show_headers=False):
    cur = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
    cur.execute(query.replace('{|schema|}', app.config['DB_SCHEMA']), args)
    if show_headers:
        print([desc[0] for desc in cur.description])
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Custom manual functions
def init_db():
    db = get_db()

    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_db_load():
    db = get_db()

    with app.open_resource('data_load.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_db_manual_update():
    db = get_db()
    if os.path.isfile('data-files/db_update.sql'):
        print ("File exist")
    with app.open_resource('data-files/db_update.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Command line requests
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('init-db-load')
@with_appcontext
def init_db_load_command():
    """Clear the existing data and create new tables."""
    init_db_load()
    click.echo('Initialized the user data.')


@click.command('init-db-manual-update')
@with_appcontext
def init_db_manual_update():
    """Force an update to the SQLite Database."""
    init_db_manual_update()
    click.echo('Database updated.')

# Link command line requests to manual functions
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_load_command)
    app.cli.add_command(init_db_manual_update)
