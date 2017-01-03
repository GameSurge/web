import os

import click
from flask import current_app
from flask.cli import with_appcontext

from gsweb import db

GULP_PATH = 'node_modules/.bin/gulp'


@click.option('--watch/--no-watch', default=None,
              help='Enable or disable the watcher.  By default the watcher is active if debug is enabled.  Without the '
                   'watcher this command only builds the assets and then terminates.')
@click.option('--minify/--no-minify', default=None,
              help='Enable or disable CSS/JS minification.  By default minification is disabled if debug is enabled.')
@with_appcontext
def gulp_command(watch, minify):
    """Runs gulp to build/monitor assets."""
    if watch is None:
        watch = current_app.debug
    if minify is None:
        minify = not current_app.debug
    if not os.path.exists(GULP_PATH):
        raise click.UsageError('This command must be run from the source root')
    assets_folder = current_app.config['ASSETS_FOLDER']
    print('Assets folder: {}'.format(assets_folder))
    os.environ['GSWEB_ASSETS_FOLDER'] = assets_folder
    os.environ['GSWEB_MINIFY'] = str(int(minify))
    gulp_args = ['bootstrap-css', 'bootstrap-js', 'scss', 'js']
    if watch:
        gulp_args.append('watch')
    os.execv(GULP_PATH, [os.path.basename(GULP_PATH)] + gulp_args)


@with_appcontext
def createdb_command():
    """Creates the initial database structure.

    This command provides a quick way to setup the initial database.
    It only creates new objects; existing ones are left untouched.
    Because of this the command is best used against an empty database
    to ensure the database and the models are completely in sync.
    """
    # TODO: replace with something nicer that provides access to alembic
    # for upgrades/downgrades once we get close to a production setup
    db.create_all()
