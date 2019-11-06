import os

from flask import Flask


def create_app(test_config: dict = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, 'upscoot.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs("uploads")
    except OSError:
        pass

    load_blueprints(app)

    return app


def load_blueprints(app: Flask):
    from .home import home_blueprint
    app.register_blueprint(home_blueprint)
