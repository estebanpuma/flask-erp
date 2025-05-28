from flask_restful import fields


payment_method_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

transaction_fields = {
    "id": fields.Integer,
    "sale_order_id": fields.Integer,
    "amount": fields.Float,
    "payment_date": fields.String,
    "method_id": fields.Integer,
    "method": fields.Nested(payment_method_fields),
    "user_id": fields.Integer,
    "notes": fields.String
}


agreement_fields = {
    "id": fields.Integer,
    "sale_order_id": fields.Integer,
    "amount": fields.Float,
    "expected_date": fields.String,
    "user_id": fields.Integer,
    "notes": fields.String
}






