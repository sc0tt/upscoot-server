import os

from flask import Flask
from flask_restful import Api


def create_app(test_config: dict = None):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
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

    upload_path = os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"])

    try:
        os.makedirs(upload_path)
    except OSError:
        pass

    app.config.update(UPLOAD_PATH=upload_path)

    try:
        os.makedirs("uploads")
    except OSError:
        pass

    load_blueprints(api)

    return app


def load_blueprints(api: Api):
    from .main import upload_resource
    api.add_resource(upload_resource, "/upload")
