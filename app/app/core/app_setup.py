from ..main import app
from flask import current_app
import os

#=========== Configure App
if os.environ.get('BSRC_APP_SETTINGS'):
    print('USING SETTINGS FROM FILE: ', os.environ.get('BSRC_APP_SETTINGS'))
    app.config.from_envvar('BSRC_APP_SETTINGS') # , silent=True)
    if app.config['UPLOAD_FOLDER']:
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
else:
    print('USING DEV DEFAULT SETTINGS')
    app.config.from_mapping(
        APP_ENV=os.environ.get('BSRC_APP_SETTINGS', 'Dev'),
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        DB_HOST='localhost',
        DB_PORT=5432,
        DB_USER='admin',
        DB_PASSWORD='password',
        DB_NAME='bsrc',
        DB_SCHEMA='dev',
        UPLOAD_FOLDER=os.path.join(app.root_path, 'data_files/uploads'),
        ALLOWED_EXTENSIONS={'xls', 'xlsx'}
    )
#
# if test_config is None:
#     # load the instance config, if it exists, when not testing
#     app.config.from_pyfile('config.py', silent=True)
# else:
#     # load the test config if passed in
#     app.config.from_mapping(test_config)

# ensure the instance folder exists
# try:
#     os.makedirs(app.instance_path)
# except OSError:
#     pass
