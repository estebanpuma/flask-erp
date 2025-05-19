from flask import request

from ..core.resources import BaseGetResource, BasePatchResource, BaseDeleteResource, BasePostResource, BulkUploadBaseResource

from .services import MaterialGroupServices, MaterialServices, MaterialExcelImportService

from .schemas import material_output_fields, material_group_output_fields

from .validations import validate_material_group_data, validate_material_group_patch_data
from .validations import validate_material_data, validate_material_patch_data


class MaterialGroupGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialGroupServices.get_material_group)
    schema_list = staticmethod( lambda: MaterialGroupServices.get_list(request.args.to_dict()))
    output_fields = material_group_output_fields


class MaterialGroupPostResource(BasePostResource):
    schema = staticmethod(validate_material_group_data)
    service_create = staticmethod(MaterialGroupServices.create_material_group)
    output_fields = material_group_output_fields


class MaterialGroupPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialGroupServices.get_material_group)
    schema_validate_partial = staticmethod(validate_material_group_patch_data)
    service_patch = staticmethod(MaterialGroupServices.update)
    output_fields = material_group_output_fields


class MaterialGroupDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(MaterialGroupServices.delete)



    # material_resources.py
class MaterialGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialServices.get)
    schema_list = staticmethod( lambda: MaterialServices.get_list(request.args.to_dict()))
    output_fields = material_output_fields


class MaterialPostResource(BasePostResource):
    schema = staticmethod(validate_material_data)
    service_create = staticmethod(MaterialServices.create)
    output_fields = material_output_fields


class MaterialPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialServices.get)
    schema_validate_partial = staticmethod(validate_material_patch_data)
    service_patch = staticmethod(MaterialServices.update)
    output_fields = material_output_fields


class MaterialDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(MaterialServices.delete)


class MaterialBulkUploadResource(BulkUploadBaseResource):
    import_service = MaterialExcelImportService
    row_handler = staticmethod(MaterialExcelImportService.handle_row)