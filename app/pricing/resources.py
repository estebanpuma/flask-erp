from flask_restful import Resource

from .services import PricingServices


class PricingResource(Resource):
    def get(self):
        try:

            actual_gross_margin = PricingServices.get_active_gross_margin()
            return {"gross_margin": actual_gross_margin.value}

        except Exception as e:
            return {"error": str(e)}, 500
