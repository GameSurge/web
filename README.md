# GameSurge website

## Development

### Install

- Clone the repo and `cd` to it
- `pyvenv-3.5 .venv`
- `pip install -r requirements.txt`
- `pip install -e .`
- `npm install`
- `cp gsweb/defaults.cfg gsweb.cfg`


### Enable code style checks

- Install eslint so it's in your PATH (e.g. `sudo npm install -g eslint`)
- `pip install pep8`
- `ln -sr pre-commit.githook .git/hooks/pre-commit`

If you do not want to install eslint globally you can also install it locally,
copy the git hook instead of symlinking it and point the `ESLINT_CMD` variable
in the script to the local eslint (e.g. `node_modules/.bin/eslint`).



### Run
- `export FLASK_APP=gsweb._cliapp FLASK_DEBUG=1 GSWEB_CONFIG=/path/to/your/gsweb.cfg`
- `flask gulp` (monitors and rebuilds assets)
- `flask run --with-threads`
