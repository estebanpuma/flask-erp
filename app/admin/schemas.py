from flask_restful import reqparse, fields

# Define los campos que serán serializados
job_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'count_users_job':fields.Integer,
    'count_workers_job':fields.Integer,
    'is_active':fields.Boolean,

}




# Define los campos para serializar la relación `Role`
role_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String
}


user_fields = {
    'id': fields.Integer,
    'ci': fields.String,
    'username': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'job': fields.Nested(job_fields),  # Incluir relación con Job
    'roles': fields.List(fields.Nested(role_fields))  # Incluir la lista de roles
}

worker_fields = {
    'id': fields.Integer,
    'ci': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone': fields.String,
    'worker_type': fields.String,
    'job_id': fields.Integer,  
    'salary': fields.Float,
    'hour_rate_normal': fields.Float,
    'job':fields.Nested(job_fields),
}

job_workers_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'workers': fields.List(fields.Nested(worker_fields)),
    'description': fields.String,
    'count_users_job':fields.Integer,
    'count_workers_job':fields.Integer,
    'is_active':fields.Boolean,

}

# Define los validadores para la entrada de datos (POST, PUT)
user_parser = reqparse.RequestParser()
user_parser.add_argument('ci', type=str, required=True, help='CI is required')
user_parser.add_argument('username', type=str, required=True, help='Username is required')
user_parser.add_argument('email', type=str, required=True, help='Email is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')
user_parser.add_argument('job_code', type=str, required=True, help="Job code is required")