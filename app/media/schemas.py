from flask_restful import fields

general_image_fields = {
    "id": fields.Integer,
    "filename": fields.String,
    "is_primary": fields.Boolean,
    "url": fields.String(attribute="url"),
}

design_image_fields = {
    "id": fields.Integer,
    "filename": fields.String,
    "is_primary": fields.Boolean,
    "url": fields.String(attribute="url"),
}

media_file_fields = {
    "id": fields.Integer,
    "filename": fields.String,
    "file_path": fields.String,
    "module": fields.String,
    "mime_type": fields.String,
    "size": fields.Integer,
    "alt_text": fields.String,
    "url": fields.String(attribute="url"),
}
