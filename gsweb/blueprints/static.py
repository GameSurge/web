import os

from flask import Blueprint, send_from_directory, current_app


bp = Blueprint('static', __name__)


@bp.route('/static/v<int:version>/<path:filename>')
def file(version, filename):
    """Serve a static file using a versioned path"""
    static_folder = os.path.join(current_app.root_path, 'static')
    cache_timeout = current_app.get_send_file_max_age(filename)
    return send_from_directory(static_folder, filename, cache_timeout=cache_timeout)


@bp.route('/static/assets/v<int:version>/<path:filename>')
def asset(version, filename):
    """Serve a static file using a versioned path"""
    cache_timeout = current_app.get_send_file_max_age(filename)
    return send_from_directory(current_app.config['ASSETS_FOLDER'], filename, cache_timeout=cache_timeout)


@bp.url_defaults
def _add_static_version(endpoint, values):
    """Add the mtime as a version identifier to the path"""
    if endpoint == bp.name + '.file':
        path = os.path.join(current_app.root_path, 'static', values['filename'])
        values['version'] = os.path.getmtime(path)
    elif endpoint == bp.name + '.asset':
        path = os.path.join(current_app.config['ASSETS_FOLDER'], values['filename'])
        values['version'] = os.path.getmtime(path)
