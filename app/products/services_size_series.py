from flask import current_app

from app import db

from ..core.exceptions import ValidationError, NotFoundError, AppError
from ..core.enums import SizeCategory

from ..core.filters import apply_filters

from .models import Size, SizeSeries

from .entities_sizes import SeriesEntity, SeriesUpdateEntity, SizesUpdateEntity


class SizeSeriesService:

    @staticmethod
    def get_obj(id):
        serie = SizeSeries.query.get(id)
        if not serie:
            raise NotFoundError("La serie no existe")
        return serie
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(SizeSeries, filters)
    
    @staticmethod
    def patch_obj(serie:SizeSeries, data:dict):
        serie_updated = SeriesUpdateEntity(data).apply_changes(serie)
        try:
            db.session.commit()
            return serie_updated
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al actualizar serie. e:{str(e)}')
            raise

    @staticmethod
    def create_obj(data:dict):

        SizeSeriesService._validate_category(data.get("category"))

        print(f'data inside service: {data}')
        serie = SeriesEntity(data).to_model()
        print(f'new serie: {serie}')
        db.session.add(serie)
        
        SizeSeriesService._bulk_create_serie_sizes(serie)
        
        try:
            db.session.commit()
            return serie
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'No se pudo crear la serie. e:{e}')
            raise

    
    def _bulk_create_serie_sizes(serie: SizeSeries, step=1):
        sizes = [
                Size(value=size, category=serie.category)
                for size in range(serie.start_size, serie.end_size + 1, step)
                ]
        db.session.add_all(sizes)
        db.session.flush()
        # Asociar tallas a la serie (rellena series_sizes)
        serie.sizes.extend(sizes)

        return sizes


    @staticmethod
    def _validate_category(category):
        if category not in [c.value for c in SizeCategory]:
            raise ValidationError(f"Categoría inválida. Opciones: {[str(c.value) for c in SizeCategory]}")
        
    @staticmethod
    def delete_obj(obj):
        try:
            db.session.delete(obj)
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'No se pudo eliminar la serie. e:{str(e)}')
            raise


class SizeService:

    @staticmethod
    def get_obj(id):
        size = Size.query.get(id)
        if not size:
            raise NotFoundError("La serie no existe")
        return size
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(Size, filters)
    
    @staticmethod
    def get_sizes_by_serie(serie_id):
        serie = SizeSeriesService.get_obj(serie_id)
        if not serie:
            raise NotFoundError(f'La serie con el ID:{serie_id} no existe')
        sizes = serie.sizes
        return sizes

    @staticmethod
    def patch_obj(obj:Size, data:dict):
        size_updated = SizesUpdateEntity(data)
        size_updated = size_updated.apply_changes(obj)
        return size_updated