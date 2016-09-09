import datetime
import logging
import logging.config
import os

import yaml
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from gsweb import db
from gsweb.core.cli import gulp_command, createdb_command
from gsweb.core.csrf import csrf
from gsweb.core.login import login_manager
from gsweb.core.srvx import srvx
from gsweb.util.db import import_all_models


def create_app(config_file=None):
    """Factory to create the Flask application

    :param config_file: A python file from which to load the config.
                        If omitted, the config file must be set using
                        the ``GSWEB_CONFIG`` environment variable.
                        If set, the environment variable is ignored
    :return: A `Flask` application instance
    """
    app = Flask('gsweb')
    _setup_logger(app)
    _load_config(app, config_file)
    _setup_db(app)
    _setup_extensions(app)
    _setup_cli(app)
    _register_handlers(app)
    _register_blueprints(app)
    return app


def _setup_logger(app):
    # Create our own logger since Flask's DebugLogger is a pain
    app._logger = logging.getLogger(app.logger_name)
    try:
        path = os.environ['GSWEB_LOGGING_CONFIG']
    except KeyError:
        path = os.path.join(app.root_path, 'logging.yml')
    with open(path) as f:
        logging.config.dictConfig(yaml.load(f))


def _load_config(app, config_file):
    app.config.from_pyfile('defaults.cfg')
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('GSWEB_CONFIG')
    if not app.config['ASSETS_FOLDER']:
        app.config['ASSETS_FOLDER'] = os.path.join(app.root_path, 'static', 'assets')
    if app.config['USE_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app)


def _setup_db(app):
    # these settings should not be configurable in the config file so we
    # set them after loading the config file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
    # ensure all models are imported even if not referenced from already-imported modules
    import_all_models(app.import_name)
    db.init_app(app)


def _setup_extensions(app):
    csrf.init_app(app)
    login_manager.init_app(app)
    srvx.init_app(app)


def _setup_cli(app):
    app.cli.command('gulp')(gulp_command)
    app.cli.command('createdb', short_help='Creates the initial database structure.')(createdb_command)


def _register_handlers(app):
    @app.shell_context_processor
    def _extend_shell_context():
        ctx = {'db': db, 'srvx': srvx}
        ctx.update(db.Model._decl_class_registry)
        ctx.update((x, getattr(datetime, x)) for x in ('date', 'time', 'datetime', 'timedelta'))
        return ctx


def _register_blueprints(app):
    from gsweb.blueprints import main_bp, static_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(static_bp)
