from flask_restful import fields

canton_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "population": fields.Integer,
    "province_id": fields.Integer,
}

province_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "population": fields.Integer,
    "cantons": fields.Nested(canton_fields),
}

province_name_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "population": fields.Integer,
}

client_category_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
}


contact_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "position": fields.String,
    "notes": fields.String,
    "birth_date": fields.String,
    "client_id": fields.Integer,
}

client_fields = {
    "id": fields.Integer,
    "ruc_or_ci": fields.String,
    "name": fields.String,
    "email": fields.String,
    "client_type": fields.String,
    "address": fields.String,
    "phone": fields.String,
    "is_special_taxpayer": fields.Boolean,
    "province": fields.Nested(province_fields),
    "canton": fields.Nested(canton_fields),
    "province_id": fields.Integer,
    "canton_id": fields.Integer,
    "contacts": fields.List(fields.Nested(contact_fields)),
    "client_category": fields.Nested(client_category_fields),
    "client_category_id": fields.Integer,
    "lifecycle_status": fields.String,
}

client_image_fields = {
    "id": fields.Integer,
    "client_id": fields.Integer,
    "is_primary": fields.Boolean,
    "order": fields.Integer,
    "type": fields.String,
    "media_file_id": fields.Integer,
    "client": fields.Nested(client_fields),
    "media_file": fields.Nested(
        {
            "id": fields.Integer,
            "filename": fields.String,
            "module": fields.String,
        }
    ),
}

client_search_fields = {
    "id": fields.Integer,
    "ruc_or_ci": fields.String,
    "name": fields.String,
    "email": fields.String,
    "client_category": fields.String,
    "address": fields.String,
    "phone": fields.String,
    "is_special_taxpayer": fields.Boolean,
    "province_name": fields.String,
    "province_id": fields.Integer,
    "canton_id": fields.Integer,
}
