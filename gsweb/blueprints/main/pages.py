from flask import render_template

from gsweb.blueprints.main import bp


@bp.route('/')
def index():
    return render_template('index.html')
