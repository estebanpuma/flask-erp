# app/auth/resources.py
from flask_restful     import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask import current_app
from app.admin.models import User  # o como llames a tu modelo de usuarios


class AuthLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Usuario requerido")
        parser.add_argument("password", type=str, required=True, help="Contraseña requerida")
        args = parser.parse_args()

        user = User.query.filter_by(email=args["username"]).first()
        if not user:
            return {'msg': 'No se encontro Usuario'}
        if not user.check_password(args["password"]):
            return {"msg": "Credenciales inválidas"}, 401

        # Genera los tokens
        access_token  = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "user": {
                "id":   user.id,
                "name": user.username
            }
        }, 200
    



class AuthRefreshResource(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)
        return {'access_token': new_token}, 200
