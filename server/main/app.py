from flask_restful import Resource, reqparse
import werkzeug
from flask import url_for, current_app
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = [
    # Images
    ".jpg", ".jpeg", ".svg", ".png", ".gif",
    # Videos
    ".mp4", ".avi", ".webm", ".webp", ".mov",
    # Audio
    ".ogg", ".mp3", ".wav",
    # Documents
    ".txt", ".docx", ".xlsx", ".csv", ".pdf",
    # Archives
    ".7z", ".zip", ".tar.gz", ".tar", ".gz", ".rar"
]


class Uploader(Resource):

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        file = args['file']

        if file.filename == "":
            return {"Error": "Empty filename"}
        if file and allowed_file(file.filename):
            # Upload
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return {"url": url_for('uploaded_file', filename=filename)}

        return {"hello": "world"}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
