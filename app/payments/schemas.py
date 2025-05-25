from flask_restful import fields

# Cuotas
installment_fields = {
    "id": fields.Integer,
    "payment_plan_id": fields.Integer,
    "due_date": fields.String,
    "amount": fields.Float,
    "paid_amount": fields.Float,
    "status": fields.String,
    "paid_on": fields.String,
    "user_id": fields.Integer,
}

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
    "installments": fields.List(fields.Nested(installment_fields)),
}


transaction_fields = {
    "id": fields.Integer,
    "payment_plan_id": fields.Integer,
    "installment_id": fields.Integer,
    "amount": fields.Float,
    "payment_date": fields.String,
    "method_id": fields.Integer,
    "user_id": fields.Integer,
    "notes": fields.String
}