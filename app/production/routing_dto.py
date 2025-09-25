# dtos/routing_dto.py
from decimal import Decimal
from typing import Annotated, List

from pydantic import Field, field_validator, model_validator

from ..core.dto_base import MyBase

NodeID = Annotated[str, Field(min_length=1)]
Minutes = Annotated[Decimal, Field(gt=Decimal("0"))]
ModelID = Annotated[int, Field(gt=0)]


class NodeIn(MyBase):
    id: NodeID
    operation_id: Annotated[int, Field(gt=0)]
    ct: Minutes
    preds: List[NodeID] = Field(default_factory=list)

    @field_validator("ct", mode="before")
    @classmethod
    def parse_decimal(cls, v):
        # Acepta "2.5" o Decimal; también "2.5min"
        if isinstance(v, str) and v.endswith("min"):
            v = v[:-3]
        return Decimal(str(v))

    @field_validator("preds", mode="after")
    @classmethod
    def norm_preds(cls, v, info):
        v = list(dict.fromkeys(map(str, v)))
        self_id = str(info.data.get("id") or "")
        if self_id and self_id in v:
            raise ValueError(f"Preds no puede contener el propio id ({self_id}).")
        return v


class SaveRoutingRequest(MyBase):
    model_id: ModelID
    nodes: List[NodeIn]

    @model_validator(mode="after")
    def cross(self):
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Ids de nodos duplicados.")
        idset = set(ids)
        for n in self.nodes:
            miss = [p for p in n.preds if p not in idset]
            if miss:
                raise ValueError(f"Preds inexistentes referenciados por {n.id}: {miss}")
        return self


class SaveRoutingResponse(MyBase):
    ok: bool = True
    model_id: ModelID
    id: int
