import os

from flask import Flask


def create_app():
    if os.environ['FLASK_ENV'] == 'development':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import api
    app.register_blueprint(api.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app


app = create_app()
