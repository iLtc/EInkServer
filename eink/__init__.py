import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py')

    if app.config['ENV'] == 'development':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/local.db'.format(app.instance_path)

    from . import api
    app.register_blueprint(api.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


app = create_app()
