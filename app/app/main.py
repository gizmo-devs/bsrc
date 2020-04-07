import os
from flask import Flask, render_template

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
from .core import app_setup

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

from .core import db, auth, import_data
from .models import competition, team, user

db.init_app(app)
app.register_blueprint(auth.bp)
app.register_blueprint(competition.bp)
app.register_blueprint(team.bp)
app.register_blueprint(user.bp)
app.register_blueprint(import_data.bp)


app.add_url_rule('/', endpoint='index')

# App Errors
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('e_404.html'), 404

def internal_server_error(e):
    # note that we set the 404 status explicitly
    return render_template('e_500.html', error=e), 500

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)



# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#         UPLOAD_FOLDER=os.path.join(app.root_path, UPLOAD_FOLDER),
#         ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS
#     )
#
#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         # load the test config if passed in
#         app.config.from_mapping(test_config)
#
#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass
#
#     # a simple page that says hello
#     @app.route('/hello')
#     def hello():
#         return 'Hello, World!'
#
#
#     from . import db, auth, competition, team, user, import_data
#     db.init_app(app)
#     app.register_blueprint(auth.bp)
#     app.register_blueprint(competition.bp)
#     app.register_blueprint(team.bp)
#     app.register_blueprint(user.bp)
#     app.register_blueprint(import_data.bp)
#
#
#     app.add_url_rule('/', endpoint='index')
#
#     # App Errors
#     def page_not_found(e):
#         # note that we set the 404 status explicitly
#         return render_template('e_404.html'), 404
#
#     def internal_server_error(e):
#         # note that we set the 404 status explicitly
#         return render_template('e_500.html', error=e), 500
#
#     app.register_error_handler(404, page_not_found)
#     app.register_error_handler(500, internal_server_error)
#
#     return app

#app = create_app(None)
if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=81)
