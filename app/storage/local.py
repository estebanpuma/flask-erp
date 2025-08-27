import os
from werkzeug.utils import secure_filename
from flask import current_app
from .interface import StorageService

class LocalStorageService(StorageService):
    def save(self, module, file_stream, filename):
        filename = secure_filename(filename)
        dest = current_app.config['UPLOAD_FOLDERS'][module]
        path = os.path.join(dest, filename)
        file_stream.save(path)
        return filename

    def delete(self, module, filename):
        path = os.path.join(current_app.config['UPLOAD_FOLDERS'][module], filename)
        if os.path.exists(path):
            os.remove(path)

    def url(self, module, filename):
        return f"/static/media/{module}/{filename}"
