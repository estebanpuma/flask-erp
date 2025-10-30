from ..core.dto_base import MyBase


class ContactPatchDTO(MyBase):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    notes: str | None = None
    birth_date: str | None = None
    client_id: int | None = None


class ContactCreateDTO(MyBase):
    name: str
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    notes: str | None = None
    birth_date: str | None = None
    client_id: int


class ClientPatchDTO(MyBase):
    name: str | None = None
    ruc_or_ci: str | None = None
    client_type: str | None = None
    province_id: int | None = None
    canton_id: int | None = None
    client_category_id: int | None = None
    is_special_taxpayer: bool | None = None
    contacts: list[ContactPatchDTO] | None = None
    address: str | None = None


class ClientCreateDTO(MyBase):
    name: str
    ruc_or_ci: str
    email: str | None = None
    phone: str
    address: str
    client_type: str
    province_id: int
    canton_id: int
    client_category_id: int | None = None
    is_special_taxpayer: bool = False


class ClientCategoryPatchDTO(MyBase):
    name: str | None = None
    description: str | None = None


class ClientCategoryCreateDTO(MyBase):
    name: str
    description: str | None = None


class ClientImageCreateDTO(MyBase):
    media_ids: list[int]
    client_id: int
    type: str
    is_primary: bool = False
    order: int | None = None
