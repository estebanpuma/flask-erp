from flask_restful import fields

payment_method_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

#payment_fields

payment_plan_fields = {
    'id': fields.Integer,
    'sale_order_id': fields.Integer,
    'payment_method_id': fields.Integer,
    'total_amount': fields.String,
    'total_installments': fields.Integer,
}
