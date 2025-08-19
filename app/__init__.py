import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # Change this for production!
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'expenses.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .db import db
    db.init_app(app)

    from . import models

    from .routes import main, categories, expenses
    app.register_blueprint(main.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(expenses.bp)

    app.add_url_rule("/", endpoint="index")

    return app
