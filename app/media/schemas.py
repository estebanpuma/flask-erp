from flask_restful import fields

general_image_fields = {
    'id':         fields.Integer,
    'filename':   fields.String,
    'is_primary': fields.Boolean,
    'url':        fields.String(attribute='url')
}

design_image_fields = {
    'id':         fields.Integer,
    'filename':   fields.String,
    'is_primary': fields.Boolean,
    'url':        fields.String(attribute='url')
}

