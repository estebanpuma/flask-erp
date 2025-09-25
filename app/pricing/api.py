from flask_restful import Api

from . import pricing_bp
from .resources import PricingResource

pricing_api = Api(pricing_bp)

pricing_api.add_resource(PricingResource, "/api/v1/pricing/gross_margin")
