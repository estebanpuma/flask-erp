from .models import StockOrder, ProductionOrder, ProductionRequirement, StockOrderProductList, StockProductionRequirement, ConsolidatedProductionItem, SaleProductionRequirement
from app import db
from flask import current_app
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict
import pytz
from sqlalchemy.sql.expression import tuple_




class ProductionServices:

    @staticmethod
    def get_all_production_orders():
        po = ProductionOrder.query.all()
        return po

    @staticmethod
    def get_production_order(id):
        po = ProductionOrder.query.get_or_404(id)
        return po

    @staticmethod
    def create_production_order(code:str,
                                responsible_id:int,
                                scheduled_start_date:str,
                                scheduled_end_date:str,
                                items:list,
                                notes:str=None):
        
        """
        Crea una nueva orden de producción y actualiza el estado de los requerimientos asociados.

        :param code: Código de la orden de producción.
        :param responsible_id: ID del responsable.
        :param scheduled_start_date: Fecha programada de inicio (formato YYYY-MM-DD).
        :param scheduled_end_date: Fecha programada de fin (formato YYYY-MM-DD).
        :param items: Lista de requerimientos de producción asociados.
        :param notes: Notas adicionales (opcional).
        :raises ValueError: Si algún dato de entrada no es válido.
        :raises Exception: Si ocurre un error inesperado.
        """
        print('ingresa a createorder')
        try:

            if not items:
                raise ValueError("No se proporcionaron requerimientos para la orden de producción.")

            new_po = ProductionOrder(code=code,
                                     responsible_id=responsible_id,
                                     scheduled_start_date = scheduled_start_date,
                                     scheduled_end_date = scheduled_end_date,
                                     notes = notes)
            print('neew order: ', new_po)
            db.session.add(new_po)
            for req in items:
                requirement = ProductionRequirement.query.get(req['request_id'])
                if not requirement:
                    raise ValueError(f"Requerimiento con ID {req['request_id']} no encontrado.")
                print(requirement)
                new_po.production_requirements.append(requirement)
        
                ProductionRequestServices.update_production_request_status(req['request_id'], 'Programada')
            
            # Consolidar ítems
            print('ahora llamo a consolidar items: ', new_po.id)
            ProductionServices.consolidate_production_items(new_po.id)
            
            
            
            db.session.commit()

        except Exception as e:
            current_app.logger.warning(f'Error al crear ProductionOrder, e:{e}')
            db.session.rollback()
            raise Exception('Error al guardar orden de produccion')
        

    def generate_production_order_code():
        tz = pytz.timezone('America/Guayaquil')
        now = datetime.now(tz)
        current_year = now.year
        prefix = f"OP-{current_year}-"

        with db.session.begin_nested():  # Bloqueo transaccional
            last_order = (ProductionOrder.query
                        .filter(ProductionOrder.code.like(f"{prefix}%"))
                        .order_by(ProductionOrder.id.desc())
                        .first())
            
            if last_order:
                last_number = int(last_order.code.split("-")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            return f"{prefix}{new_number}"
        

       
    def consolidate_production_items(order_id):
        """
        Consolidar modelos, series y tallas para una orden de producción específica.
        """
        try:
            # Obtener la orden de producción
            production_order = ProductionServices.get_production_order(order_id)
            if not production_order:
                raise ValueError(f'ProductionOrder {order_id} no encontrado')

            # Eliminar consolidaciones existentes
            ProductionServices.delete_existing_consolidations(order_id)

            # Obtener datos consolidados
            sales_items = ProductionServices.get_consolidated_items_from_sales(production_order)
            stock_items = ProductionServices.get_consolidated_items_from_stock(production_order)
            # Consolidar los datos
            consolidated_data = ProductionServices.merge_consolidated_data(sales_items, stock_items)
 
            # Guardar datos consolidados
            ProductionServices.save_consolidated_data(order_id, consolidated_data)

        except Exception as e:
            ProductionServices.handle_exception(e)


    # Subfunciones para modularizar el código


    def delete_existing_consolidations(order_id):
        """Elimina las consolidaciones existentes para la orden de producción."""
        ConsolidatedProductionItem.query.filter_by(production_order_id=order_id).delete()

    def get_consolidated_items_from_sales(production_order):
        """Obtiene los datos consolidados de los requerimientos de venta."""
        from sqlalchemy import func
        return []
        #return db.session.query(
            #SaleOrderProductList.product_code,
            ##SaleOrderProductList.product_serie,
            #SaleOrderProductList.product_size,
            #func.sum(SaleOrderProductList.product_qty).label('total_qty')
        #).join(
            #SaleProductionRequirement, SaleProductionRequirement.sale_order_id == #SaleOrderProductList.sale_order_id
       # ).filter(
           # SaleProductionRequirement.production_order.contains(production_order)
       # ).group_by(
            #SaleOrderProductList.product_code, SaleOrderProductList.product_serie, SaleOrderProductList.product_size
        #).all()

    def get_consolidated_items_from_stock(production_order):
        """Obtiene los datos consolidados de los requerimientos de stock."""

        from ..products.models import Product
        # Paso 1: Seleccionar campos necesarios, incluyendo el code
        filtered_query = db.session.query(
            StockOrderProductList.product_id,
            Product.code,  # Aquí incluimos el model_code
            StockOrderProductList.product_serie,
            StockOrderProductList.product_size,
            func.sum(StockOrderProductList.product_qty).label('total_qty')
        ).join(
            StockProductionRequirement,
            StockProductionRequirement.stock_order_id == StockOrderProductList.stock_order_id
        ).join(
            Product,  # Unimos con la tabla Product para obtener el model_code
            Product.id == StockOrderProductList.product_id
        ).filter(#filtro los datos para la orden de produccion actual
            StockProductionRequirement.production_order.contains(production_order)
        )

        # Paso 2: Agrupar los datos
        grouped_query = filtered_query.group_by(
            StockOrderProductList.product_id,
            Product.code,  # Agrupamos también por model_code
            StockOrderProductList.product_serie,
            StockOrderProductList.product_size
        )

        # Paso 3: Ejecutar el query y obtener los resultados
        items = grouped_query.all()

        return items
        

    def merge_consolidated_data(sales_items, stock_items):
        """Fusiona los datos de ventas y stock en un único diccionario consolidado."""
        consolidated_data = {}
        for item in sales_items + stock_items:
            key = (item.product_id, item.code, item.product_serie, item.product_size)
            consolidated_data[key] = consolidated_data.get(key, 0) + item.total_qty

        return consolidated_data

    def get_consolidated_items(order_id):
        """
        Obtener ítems consolidados para una orden de producción.
        """
        consolidated_items = ConsolidatedProductionItem.query.filter_by(production_order_id=order_id).all()

        return consolidated_items

    def save_consolidated_data(order_id, consolidated_data):
        """Guarda los datos consolidados en la base de datos."""
        try:
            for (id, code, series, size), total_quantity in consolidated_data.items():
                consolidated_item = ConsolidatedProductionItem(
                    model_id = id,
                    production_order_id=order_id,
                    model_code=code,
                    series=series,
                    size=size,
                    total_quantity=total_quantity
                )
                db.session.add(consolidated_item)
            db.session.commit()
        except Exception as e:
            current_app.logger.warning('Error al consolidar datos')
            db.session.rollback()
            raise Exception(e)

    def handle_exception(exception):
        """Maneja las excepciones y realiza un rollback."""
        current_app.logger.warning(f'Error al consolidar datos: {exception}')
        db.session.rollback()


    def get_consolidated_order_materials(order_id):
        # Obtener los ítems consolidados
        items = ProductionServices.get_consolidated_items(order_id)

        # Crear una lista con los datos relevantes (model_id, series, qty)
        consolidated_items = [(item.model_id, item.series, item.total_quantity) for item in items]
        print(consolidated_items)
        # Crear un diccionario para almacenar las sumas
        sums = {}

        # Iterar sobre la lista y sumar los valores
        for item in consolidated_items:
            key = (item[0], item[1])  # Clave basada en los dos primeros valores
            if key in sums:
                sums[key] += item[2]  # Sumar el tercer valor
            else:
                sums[key] = item[2]  # Iniciar la suma si no existe la clave

        # Convertir el resultado de nuevo a una lista de tuplas
        result = [(key[0], key[1], total) for key, total in sums.items()]
                # Llamar a la función optimizada para obtener los materiales
        print('ahora result: ', result)
        order_materials = ProductionServices.get_product_materials(result)
        
        return order_materials

        
    from sqlalchemy.sql.expression import tuple_

    def get_product_materials(items: list):
        from ..products.models import ProductMaterialDetail, Material

        bom = []
        for item in items:

        # Construir la consulta para obtener los materiales necesarios
            query = (
                db.session.query(
                    ProductMaterialDetail.material_id,
                    Material.code,
                    Material.name,
                    Material.unit,
                    ProductMaterialDetail.serie_id,
                    ProductMaterialDetail.quantity * item[2]
                    )
                .join(Material, Material.id == ProductMaterialDetail.material_id)
                .filter(
                    ProductMaterialDetail.product_id == item[0],
                    ProductMaterialDetail.serie_id == 13,
                )
                .all()
            )
            print('query: ', query, 'type: ', type(query))
            material = {
                query
            }
            bom.append(material)

        print('Resultado del boom:', bom)

        


        materials = []
        # Devuelvo los resultados para que los puedas procesar
        return materials



    

    def delete_production_order(order_id:int):
        '''Elimina las ordenes de produccion'''
        try:
            order = ProductionServices.get_production_order(order_id)
            requirements = order.production_requirements
            for r in requirements:
                ProductionRequestServices.update_production_request_status(r.id, 'Pendiente')
            db.session.delete(order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al eliminar la orden de produccion e:{e}')
            raise
        

class StockOrderServices:

    @staticmethod
    def get_all_stock_orders():
        stock_orders = StockOrder.query.all()
        return stock_orders

    @staticmethod
    def get_stock_order(stock_order_id:int):
        stock_order = StockOrder.query.get_or_404(stock_order_id)
        return stock_order
    
    @staticmethod
    def get_next_so_code():
        try:
            last_stock_order = StockOrder.query.order_by(StockOrder.id.desc()).first()
            print(last_stock_order)
            if last_stock_order:
                last_stock_order_number = int(last_stock_order.stock_order_code)
                new_code = last_stock_order_number +1
            else:
                new_code = 1
            return str(new_code)
        except Exception as e:
            current_app.logger.warning(f'Error al obtener next code stockorder. e:{e}')
            raise Exception(str(e))


    def create_stock_order(stock_order_code:str, 
                           request_date:str,
                           delivery_date:str,
                           responsible_id:int,
                           notes:str,
                           items):
        """
        Crea un registro de StockOrder y sus relaciones asociadas (productos y requerimientos).
        """
        
        new_stock_order = StockOrder(stock_order_code=stock_order_code,
                                     request_date=request_date,
                                     delivery_date=delivery_date,
                                     responsible_id=responsible_id,
                                     notes=notes
                                     )
        
        try:
            db.session.add(new_stock_order)
            db.session.flush()
            # Crear la lista de productos relacionados
            StockOrderServices.create_stock_order_product_list(new_stock_order.id, items)
            # Crear el requerimiento de producción relacionado
            StockOrderServices.create_stock_production_requirement(new_stock_order.id)
            # Confirmar la transacció
            db.session.commit()
            current_app.logger.info(f'Orden de Stock N. {stock_order_code} creada')
            current_app.logger.info(f'Requerimiento de produccion creado')
            return new_stock_order
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'No se puede crear la orden de stock. e:{e}' )
            raise Exception(f'Error al crear StockOrder. e:{str(e)}')


    def create_stock_production_requirement(stock_order_id):
        from .models import StockProductionRequirement,ProductionRequirement
        try:

            # Crear el StockProductionRequirement asociado
            new_stock_requirement = StockProductionRequirement(
                stock_order_id=stock_order_id
            )
            db.session.add(new_stock_requirement)
        except Exception as e:
            raise Exception(f'error al crear StockProductionRequirement. e:{e}')
    
    def create_stock_order_product_list(stock_order_id:int, items):
        from .models import StockOrderProductList
        from ..products.models import Product
        from ..products.services import SeriesServices
        try:
            if items:
                product_list = []
                for item in items:
                    product = Product.query.filter_by(code = item['code']).first()
                    serie = SeriesServices.get_serie_by_size(item['size'])
                    new_product = StockOrderProductList(stock_order_id=stock_order_id, 
                                                        product_id=product.id,
                                                        product_size = str(item['size']),
                                                        product_serie = serie,
                                                        product_qty = item['qty'],
                                                        )
                    product_list.append(new_product)
                
                db.session.add_all(product_list)

        except Exception as e:
            current_app.logger.warning(f'Error al guardar producto de order de stock. e:{e}')
            raise Exception(f'Error al guardar productos del StockOrder. e:{str(e)}')
                

    @staticmethod
    def delete_stock_order(stock_order_id):
        try:
            stock_order = StockOrder.query.get_or_404(stock_order_id)

            db.session.delete(stock_order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al eliminar StockOrder. e:{e}')
            raise Exception(str(e))
        

class ProductionRequestServices:

    @staticmethod
    def get_all_production_requests():
        from .models import ProductionRequirement, SaleProductionRequirement, StockProductionRequirement
        

        try:
            requirements = ProductionRequirement.query.options(
                joinedload('*')  # Cargar subclases relacionadas
            ).all()

            # Estructurar datos para el usuario
            result = []
            for requirement in requirements:
                req_data = {
                    "id": requirement.id,
                    "type": requirement.type,
                    "status": requirement.status,
                }
                if isinstance(requirement, SaleProductionRequirement):
                    req_data.update({
                        "order_number": requirement.sale_order_id,
                        "request_date": '',
                        "order_type": "Venta",
                        "responsible": 'Vendor',
                    })
                elif isinstance(requirement, StockProductionRequirement):
                    req_data.update({
                        "order_number": requirement.stock_order.stock_order_code,
                        "request_date": requirement.stock_order.request_date.isoformat(),
                        "order_type": "Inventario",
                        "responsible": requirement.stock_order.responsible.username,  # Ejemplo
                    })
                result.append(req_data)
            return result
        except Exception as e:
            current_app.logger.warning(f"Error al cargar ProductionRequeriments. e:{e}")
            raise Exception(f'Error: {e}')
        

    @staticmethod
    def get_production_request(production_request_id):
        from .models import ProductionRequirement, StockProductionRequirement, StockOrder
        from ..products import Product

        try:
            # Obtener el requerimiento base
            requirement = ProductionRequirement.query.get_or_404(production_request_id)

            # Construir la respuesta base
            req_data = {
                "id": requirement.id,
                "type": requirement.type,
                "status": requirement.status,
            }

            # Si es un requerimiento de inventario (StockProductionRequirement)
            if isinstance(requirement, StockProductionRequirement):
                # Usar la relación para evitar una segunda consulta
                stock_order = requirement.stock_order

                product_ids = [model.product_id for model in stock_order.stock_order_product_list]
                products = Product.query.filter(Product.id.in_(product_ids)).all()
                product_dict = {product.id: product.code for product in products}  # Mapear IDs a códigos


                req_data.update({
                    "order_number": stock_order.stock_order_code,
                    "request_date": stock_order.request_date.isoformat(),  
                    "order_type": "Inventario",
                    "responsible": stock_order.responsible.username,  # Asumiendo que hay una relación con usuario
                    "notes": stock_order.notes,
                    "models": [
                        {
                            "product_id": model.product_id,
                            "product_code": product_dict.get(model.product_id, "N/A"),  # Buscar código en el mapeo
                            "product_size": model.product_size,
                            "product_qty": model.product_qty,
                            "notes": model.notes,
                        }
                        for model in stock_order.stock_order_product_list
                    ]
                })

            return req_data

        except Exception as e:
            current_app.logger.warning(f"Error al cargar ProductionRequirement. Detalles: {e}")
            raise Exception(f"Error al obtener el requerimiento: {e}")


    @staticmethod
    def update_production_request_status(id:int, status:str):
        """
        Actualiza el estado de una requisición de producción y su porden asociada

        :param id: ID de la requisición de producción.
        :param status: Nuevo estado para la requisición.
        :raises ValueError: Si el estado no es válido.
        :raises Exception: Si ocurre un error inesperado.
        """
        status_options = ['Programada', 'Diferida', 'Rechazada', 'En progreso', 'Completada', 'Pendiente']
        if status not in status_options:
            raise ValueError(f"Estado inválido: '{status}'. Opciones válidas: {status_options}")

        try:
            # Buscar la requisición por ID
            pr = ProductionRequirement.query.get_or_404(id)
            if not pr:
                raise ValueError(f"No se encontró una requisición de producción con ID {id}.")
            stock_order = StockOrderServices.get_stock_order(pr.stock_order_id)
            if not stock_order:
                raise ValueError(f"No se encontró una orden de produccion con ID {pr.stock_order_id}.")
            # Actualizar el estado
            pr.status = status
            stock_order.status = status
            
        except ValueError as ve:
            # Re-lanzar errores de validación con detalles
            current_app.logger.warning(f"Error de validación al actualizar el estado: {ve}")
            raise ve
        except Exception as e:
            # Manejo de errores genéricos
            current_app.logger.error(f"Error inesperado al actualizar requisición de producción. e:{e}")
            raise Exception(f"Error al actualizar el estado: {e}")
     