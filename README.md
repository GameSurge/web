# GameSurge website

## Development

### Install

- Clone the repo and `cd` to it
- `pyvenv-3.5 .venv`
- `pip install -r requirements.txt`
- `pip install -e .`
- `npm install`
- `cp gsweb/defaults.cfg gsweb.cfg`

### Run
- `export FLASK_APP=gsweb._cliapp FLASK_DEBUG=1 GSWEB_CONFIG=/path/to/your/gsweb.cfg`
- `flask gulp` (monitors and rebuilds assets)
- `flask run --with-threads`
