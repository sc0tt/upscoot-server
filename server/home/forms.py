from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, PasswordField
from wtforms.fields.html5 import URLField


class UploadForm(FlaskForm):
    file = FileField('file')
    url = URLField('url')
    password = PasswordField('pass')
    private = BooleanField('private')
