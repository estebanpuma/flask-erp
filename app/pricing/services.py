from flask import current_app

from app import db

from datetime import datetime
from .models import GrossMargin


class PricingServices:

    def create_gross_margin(value: float, notes: str=None):
        try:
            print('value', value)
            # Deactivate existing active margins
            existing_active_margins = GrossMargin.query.filter_by(is_active_margin=True).all()
            for margin in existing_active_margins:
                margin.is_active_margin = False
                db.session.add(margin)

            margin = GrossMargin(value=value, 
                                notes=notes,
                                begin_date=datetime.now(),
                                is_active_margin=True)
            db.session.add(margin)
            print('control 1 tod bien')
            PricingServices.update_product_prices(value)
            db.session.commit()
            return margin
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error creating gross margin: {e}')
            raise e
    
    def update_product_prices(value: float):
        try:
            
            from ..products.services import ProductServices
            # Get all products
            products = ProductServices.get_all_products()
            for product in products:

                
                # Get current price
                current_material_cost = ProductServices.calculate_material_cost(product.id)['material_cost']
                print('in update material cost:', current_material_cost)
                # Calculate new price
                new_price = current_material_cost / (1 - (value / 100))               
                # Create new price history
                product.pvp = new_price
                db.session.add(product)
        except Exception as e:  
            current_app.logger.warning(f'Error updating product prices: {e}')
            raise e
        

    def get_gross_margin(self, margin_id):
        return GrossMargin.query.get_or_404(margin_id)
    
    def get_active_gross_margin():
        return GrossMargin.query.filter_by(is_active_margin=True).first()