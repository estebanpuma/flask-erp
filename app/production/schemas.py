from flask_restful import fields, reqparse


stock_prod_order_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'request_date': fields.DateTime,
    'responsible_id': fields.String,
    'status': fields.String,
    'notes': fields.String
 
}