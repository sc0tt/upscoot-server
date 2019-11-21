import mimetypes
import os
import random
import string

import magic
import redis
import requests
from flask import Blueprint, render_template, redirect, url_for, current_app, send_from_directory

from .forms import UploadForm

blueprint = Blueprint("home", __name__)


@blueprint.route("/")
def index():
    form = UploadForm()
    return render_template("home.html", form=form)


@blueprint.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_PATH"], filename)


@blueprint.route("/upload", methods=["POST"])
def upload():
    form = UploadForm()
    # Verify password
    if form.validate_on_submit() and current_app.config["UPLOAD_PASSWORD"] == form.password.data:
        redis_config = current_app.config["REDIS_CONFIG"]
        if redis_config:
            redis_client = redis.Redis(**redis_config, decode_responses=True)
        else:
            redis_client = None

        if form.file.data:
            # TODO: Consolidate code since a lot of this is repeated
            # Try and get the extension from the filename. If that fails use magic to figure it out.
            file_ext = os.path.splitext(form.file.data.filename)[1]
            if not file_ext:
                magic_instance = magic.Magic(mime=True)
                mime_type = magic_instance.from_buffer(form.file.data.stream.read())
                file_ext = mimetypes.guess_extension(mime_type, strict=True)
            file_name = get_filename(file_ext, form.private.data)
            file_path = os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            if not file_ext:
                # TODO: Flash error
                return redirect(url_for('home.index'))

            form.file.data.save(file_path)

            if not form.private.data and redis_client:
                redis_client.publish(current_app.config["REDIS_CHANEL"],
                                     url_for('home.uploaded_file', filename=file_name,
                                             _external=True))

                return redirect(url_for('home.uploaded_file', filename=file_name))
            elif form.url.data:
                # download file if file is URL
                download_request = requests.get(form.url.data, stream=True)
                if not download_request.ok:
                    # TODO: Flash error
                    return redirect(url_for('home.index'))
                content_type = download_request.headers["Content-Type"]
                # TODO: First try and get the extension from the url
                file_ext = mimetypes.guess_extension(content_type, strict=True)
                if not file_ext:
                    # TODO: Flash error
                    return redirect(url_for('home.index'))

                # TODO: Validate size against max allowable
                # content_len = download_request.headers["Content-Length"]
                file_name = get_filename(file_ext, form.private.data)
                file_path = os.path.join(current_app.config["UPLOAD_PATH"], file_name)
                with open(file_path, "wb") as out_file:
                    for block in download_request.iter_content(1024):
                        if not block:
                            break
                        out_file.write(block)

                if not form.private.data and redis_client:
                    redis_client.publish(current_app.config["REDIS_CHANEL"],
                                         url_for('home.uploaded_file', filename=file_name, _external=True))

                    return redirect(url_for('home.uploaded_file', filename=file_name))
                else:
                    # TODO: Flash error
                    return redirect(url_for('home.index'))

                # Create new filename, this will need validation at some point so there are no dupes.
                pass

            return redirect(url_for('home.index'))


def get_filename(extension: str, private: bool):
    # Create new filename, this will need validation at some point so there are no dupes.
    filename = ''.join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))

    # prefix filename with _ if private
    return "{}{}{}".format("_" if private else "", filename, extension)
