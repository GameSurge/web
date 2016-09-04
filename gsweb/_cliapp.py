# XXX: Never import this package. It only exists so the `flask`
# command can use it (using `FLASK_APP=gsweb._cliapp`) as it cannot
# use an app factory directly

from gsweb.core.app import create_app

app = create_app()
