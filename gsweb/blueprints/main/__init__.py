from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

# Import the modules containing the view functions down here so these
# modules can import the blueprint from here
from . import pages  # noqa
