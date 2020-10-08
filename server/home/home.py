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
    """
    --> passcode, private, image, url

    <-- redirect uri
    """
    form = UploadForm()
    # Verify password
    if form.validate_on_submit() and current_app.config["UPLOAD_PASSWORD"] == form.password.data:
        redis_config = current_app.config["REDIS_CONFIG"]
        if redis_config:
            redis_client = redis.Redis(**redis_config, decode_responses=True)
        else:
            redis_client = None

        max_size = current_app.config["MAX_UPLOAD_SIZE_BYTES"]
        if form.file.data:
            # TODO: Consolidate code since a lot of this is repeated
            # Try and get the extension from the filename. If that fails use magic to figure it out.
            file_ext = os.path.splitext(form.file.data.filename)[1]
            content_type = form.file.data.content_type
            print(f"File extension: {file_ext}")

            # Extension couldn't be determined from the filename, attempt using the headers.
            if not file_ext and content_type:
                file_ext = mimetypes.guess_extension(content_type, strict=True)
                print(f"Guessing file extension from headers: {file_ext}")

            # Extension couldn't be determined from the filename or the headers, try reading the data.
            if not file_ext:
                magic_instance = magic.Magic(mime=True)
                mime_type = magic_instance.from_buffer(form.file.data.stream.read())
                file_ext = mimetypes.guess_extension(mime_type, strict=True)
                print(f"Guessing file extension from buffer: {file_ext}")

            if not file_ext:
                # TODO: Flash error
                print(f"Invalid file extension: {file_ext}")
                return redirect(url_for('home.index'))

            file_name = get_filename(file_ext, form.private.data)
            file_path = os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            form.file.data.save(file_path)
            file_size = os.path.getsize(file_path)
            if file_size > max_size or file_size <= 0:
                print("Upload size invalid")
                if os.path.exists(file_path):
                    os.remove(file_path)

            if not form.private.data and redis_client.connection:
                redis_client.publish(current_app.config["REDIS_CHANNEL"],
                                     url_for('home.uploaded_file', filename=file_name,
                                             _external=True))

            return redirect(url_for('home.uploaded_file', filename=file_name))
        elif form.url.data:
            print("URL: " + form.url.data)
            # download file if file is URL
            download_request = requests.get(form.url.data, stream=True)
            if not download_request.ok:
                # TODO: Flash error
                print("Download request failed.")
                return redirect(url_for('home.index'))

            content_len = int(download_request.headers["Content-Length"] or 0)

            # Do first size check before downloading
            if content_len > max_size or content_len <= 0:
                # TODO: Flash error
                print("Upload size invalid")
                return redirect(url_for('home.index'))

            print(f"Content-Length: {content_len}")

            content_type = download_request.headers["Content-Type"]
            file_ext = mimetypes.guess_extension(content_type, strict=True)
            if not file_ext:
                # TODO: Flash error
                print("Unknown file extension")
                return redirect(url_for('home.index'))

            file_name = get_filename(file_ext, form.private.data)
            file_path = os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            downloaded_size = 0

            try:
                with open(file_path, "wb") as out_file:
                    for block in download_request.iter_content(1024, decode_unicode=True):
                        if not block:
                            break
                        out_file.write(block)
                        downloaded_size += len(block)
                        # Second size check occurs while downloading.
                        if downloaded_size > max_size:
                            raise UploadSizeException
            except UploadSizeException:
                print("Upload size exceeded")
                if os.path.exists(file_path):
                    os.remove(file_path)

            if not form.private.data and redis_client.connection:
                redis_client.publish(current_app.config["REDIS_CHANNEL"],
                                     url_for('home.uploaded_file', filename=file_name, _external=True))

            return redirect(url_for('home.uploaded_file', filename=file_name))
        return redirect(url_for('home.index'))


def get_filename(extension: str, private: bool):
    # Create new filename, this will need validation at some point so there are no dupes.
    filename = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))

    # prefix filename with _ if private
    return "{}{}{}".format("_" if private else "", filename, extension)


class UploadSizeException(Exception):
    pass
