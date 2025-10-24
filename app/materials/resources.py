from flask import request
from flask_restful import Resource, marshal

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
    BulkUploadBaseResource,
)
from ..core.utils import success_response
from .material_group_services import MaterialGroupService, MaterialSubGroupService
from .material_services import MaterialService, MaterialStockService
from .schemas import (
    material_group_output_fields,
    material_output_fields,
    material_search_fields,
    material_stock_fields,
    material_subgroup_output_fields,
)
from .services import MaterialExcelImportService


class MaterialGroupGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialGroupService.get_obj)
    schema_list = staticmethod(
        lambda: MaterialGroupService.get_obj_list(request.args.to_dict())
    )
    output_fields = material_group_output_fields


class MaterialGroupPostResource(BasePostResource):
    service_create = staticmethod(MaterialGroupService.create_obj)
    output_fields = material_group_output_fields


class MaterialGroupPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialGroupService.get_obj)
    service_patch = staticmethod(MaterialGroupService.pacth_obj)
    output_fields = material_group_output_fields


class MaterialGroupDeleteResource(BaseDeleteResource):
    service_get = staticmethod(MaterialGroupService.get_obj)
    service_delete = staticmethod(MaterialGroupService.delete_obj)


# ----------------Material SubGroups---------------------------
class MaterialSubGroupGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialSubGroupService.get_obj)
    output_fields = material_subgroup_output_fields


class MaterialSubGroupPostResource(BasePostResource):
    service_create = staticmethod(MaterialSubGroupService.create_obj)
    output_fields = material_subgroup_output_fields


class MaterialSubGroupPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialSubGroupService.get_obj)
    service_patch = staticmethod(MaterialSubGroupService.patch_obj)
    output_fields = material_subgroup_output_fields


class MaterialSubGroupDeleteResource(BaseDeleteResource):
    service_get = staticmethod(MaterialSubGroupService.get_obj)
    service_delete = staticmethod(MaterialSubGroupService.delete_obj)


class MaterialGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialService.get_obj)
    schema_list = staticmethod(
        lambda: MaterialService.get_obj_list(request.args.to_dict())
    )
    output_fields = material_output_fields


class MaterialSearchResource(Resource):
    def get(self):
        args = request.args.to_dict()
        if "q" in args:
            try:
                print(args)
                materials = MaterialService.search_material(str(args["q"]))
                print(f"materils {materials}")
                return success_response(marshal(materials, material_search_fields))
            except Exception as e:
                raise e


class MaterialPostResource(BasePostResource):
    service_create = staticmethod(MaterialService.create_obj)
    output_fields = material_output_fields


class MaterialPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialService.get_obj)
    service_patch = staticmethod(MaterialService.patch_obj)
    output_fields = material_output_fields


class MaterialDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(MaterialService.delete_obj)


class MaterialBulkUploadResource(BulkUploadBaseResource):
    import_service = MaterialExcelImportService
    row_handler = staticmethod(MaterialExcelImportService.handle_row)


class MaterialTotalStockResource(Resource):
    def get(self, material_id):
        total = MaterialStockService.get_total_stock(material_id)
        return {"material_id": material_id, "total_stock": total}, 200


class MaterialStockGetResource(BaseGetResource):
    schema_list = staticmethod(
        lambda: MaterialStockService.get_obj_list(request.args.to_dict())
    )
    output_fields = material_stock_fields
