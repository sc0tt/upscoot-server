from flask import Blueprint, render_template, redirect, url_for
from .forms import UploadForm
import magic
import mimetypes

blueprint = Blueprint("home", __name__)


@blueprint.route("/")
def index():
    form = UploadForm()
    return render_template("home.html", form=form)


@blueprint.route("/upload", methods=["POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Verify password
        # determine file extension
        # Create new filename
        # prefix filename with _ if private
        # download file if file is URL
        # save file locally
        # redirect to file

        # Testing mimetype detection for files without an extension
        # print(form.file.data.content_type)
        # f = magic.Magic(mime=True)
        # mimetype = f.from_buffer(form.file.data.stream.read())
        # print(mimetype)
        # print(mimetypes.guess_extension(mimetype, strict=True))
        pass

    return redirect(url_for('home.index'))
