from app import db

from ..common import BaseModel


class MediaFile(BaseModel):
    """
    Modelo genérico para almacenar información sobre cualquier archivo subido.
    """

    __tablename__ = "media_files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(255), nullable=False)
    module = db.Column(
        db.String(50), nullable=False, index=True
    )  # ej: 'designs', 'products'
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)  # en bytes
    alt_text = db.Column(db.String(255))

    @property
    def url(self):
        """Genera la URL pública para acceder al archivo."""
        return f"/api/v1/media/img/{self.module}/{self.filename}"

    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}')>"
