import os

from flask import Flask


def create_app(test_config: dict = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'upscoot.sqlite')  # This will move to config file eventually.
    )

    if test_config is None:
        app.config.from_object('config')  # Load default settings
        app.config.from_pyfile('config.py', silent=True)  # load application specific settings
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs("uploads")
    except OSError:
        pass

    load_blueprints(app)

    return app


def load_blueprints(app: Flask):
    from .home import home_blueprint
    app.register_blueprint(home_blueprint)
