from flask_restful import request

from ..core.resources import BaseGetResource


class SecuenceResource(BaseGetResource):
    def get(self):
        from .services import SecuenceGenerator

        q = request.args.to_dict()
        return SecuenceGenerator.set_obj(q)
