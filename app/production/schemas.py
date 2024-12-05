from flask_restful import fields, reqparse


stock_order_product_list_fields = {
    'id': fields.Integer,
    'stock_order_id': fields.Integer,
    'product_id': fields.String,
    'product_size': fields.Integer,
    'product_qty': fields.Integer,
    'notes': fields.String
}


stock_order_with_products_fields = {
    'id': fields.Integer,
    'stock_order_code': fields.String,
    'request_date': fields.String,
    'delivery_date':fields.String,
    'responsible_id': fields.Integer,
    'status': fields.String,
    'notes': fields.String,
    'stock_order_product_list': fields.List(fields.Nested(stock_order_product_list_fields)) 
 
}

stock_order_simple_fields = {
    'id': fields.Integer,
    'stock_order_code': fields.String,
    'request_date': fields.String,
    'delivery_date':fields.String,
    'responsible_id': fields.Integer,
    'status': fields.String,
    'notes': fields.String,
 
}


production_requirement_fields={
    'id':fields.Integer,
    'order_number': fields.Integer,
    'type': fields.String

}


production_order_fields ={
    'id': fields.Integer,
    'code': fields.String,
    'scheduled_start_date': fields.String,
    'scheduled_end_date': fields.String,
    'actual_start_date': fields.String,
    'actual_end_date': fields.String,
    'responsible_id': fields.Integer,
    'status': fields.String,
    'notes': fields.String,
    'production_requirements': fields.List(fields.Nested(production_requirement_fields))

}


consolidated_items_fields = {
    'id': fields.Integer,
    'production_order_id': fields.Integer,
    'model_code': fields.String,
    'series': fields.String,
    'size': fields.Integer,
    'total_quantity': fields.Integer
}