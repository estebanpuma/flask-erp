from app import db

from flask import current_app

from .models import Product, ProductLine, ProductSubLine

class ProductServices:

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return products
    
    @staticmethod
    def get_product(product_id):
        product = Product.query.get_or_404(product_id)
        return product
    
    @staticmethod
    def create_product(line_id, code, name, subline_id=None, description=None, files=None):
        line = ProductLine.query.get_or_404(line_id)
        if line:
            try:
                new_product = Product(code = code,
                                      name = name,
                                      description = description,
                                      line_id = line_id,
                                      subline_id = subline_id)
                db.session.add(new_product)
                db.session.commit()
                current_app.logger.info(f'Producto {new_product.name} creado')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error creando producto: {str(e)}')

    
    @staticmethod
    def get_all_lines():
        lines = ProductLine.query.all()
        return lines
    
    @staticmethod
    def get_line(line_id):
        line = ProductLine.query.get_or_404(line_id)
        return line

    @staticmethod
    def get_all_sublines():
        sublines = ProductSubLine.query.all()
        return sublines
    
    @staticmethod
    def get_subline(subline_id):
        subline = ProductSubLine.query.get_or_404(subline_id)
        return subline