from .. import db
from ..core.exceptions import NotFoundError
from ..products.models import Product
from .models import (
    OperationRouting,
    OperationRoutingEdge,
    OperationRoutingNode,
    OperationRoutingStep,
)
from .routing_domain import Routing
from .routing_dto import SaveRoutingRequest, SaveRoutingResponse


class OperationRoutingService:

    @staticmethod
    def _get_model_or_404(model_id: int):
        m = db.session.query(Product).get(model_id)
        if not m:
            raise NotFoundError(f"Modelo no encontrado (id={model_id}).")
        return m

    @staticmethod
    def create_obj(data: dict) -> SaveRoutingResponse:
        with db.session.begin():
            routing = OperationRoutingService.save(data)
            return routing

    @staticmethod
    def preview(data: dict) -> dict:
        """
        Stateless: valida DTO, calcula con dominio y devuelve métricas.
        NO guarda nada en DB.
        """
        dto = SaveRoutingRequest.model_validate(data)  # model_id + nodes (Decimal)
        routing = Routing.from_dto(dto.model_id, [n.model_dump() for n in dto.nodes])
        metrics = routing.compute()  # llena es/ef/ls/lf/slack/crit/level en nodes

        nodes_out = [
            {
                "id": n.key,
                "es": str(n.es),
                "ef": str(n.ef),
                "ls": str(n.ls),
                "lf": str(n.lf),
                "slack": str(n.slack),
                "crit": bool(n.crit),
            }
            for n in routing.nodes
        ]

        return {
            "ok": True,
            "errors": [],
            "metrics": {
                "lt": str(metrics.lt),
                "bottleneck_key": metrics.bottleneck_key,
                "nodes": nodes_out,
                "levels": metrics.levels,
            },
        }

    @staticmethod
    def save(data: dict) -> SaveRoutingResponse:
        with db.session.begin():
            dto = SaveRoutingRequest.model_validate(data)
            OperationRoutingService._get_model_or_404(dto.model_id)

            # 1) Dominio: construir y calcular
            routing = Routing.from_dto(
                dto.model_id, [n.model_dump() for n in dto.nodes]
            )
            metrics = routing.compute()  # llena es/ef/ls/lf/slack/crit/level en nodes
            steps = routing.to_linear_steps()

            # 2) UPSERT por model_id (simple: reemplazar todo el grafo)

            row = (
                db.session.query(OperationRouting)
                .filter_by(model_id=dto.model_id)
                .first()
            )
            if row is None:
                row = OperationRouting(model_id=dto.model_id)
                db.session.add(row)
                db.session.flush()
            # limpia “hijos”
            db.session.query(OperationRoutingEdge).filter_by(routing_id=row.id).delete()
            db.session.query(OperationRoutingStep).filter_by(routing_id=row.id).delete()
            db.session.query(OperationRoutingNode).filter_by(routing_id=row.id).delete()
            db.session.flush()

            # 3) insertar nodos
            # Mapa key → node_id DB
            key2id = {}
            for n in routing.nodes:
                rec = OperationRoutingNode(
                    routing_id=row.id,
                    node_key=n.key,
                    operation_id=n.operation_id,
                    ct=n.ct,
                    es=n.es,
                    ef=n.ef,
                    ls=n.ls,
                    lf=n.lf,
                    slack=n.slack,
                    crit=n.crit,
                    level=n.level,
                )
                db.session.add(rec)
                db.session.flush()
                key2id[n.key] = rec.id

            # 4) insertar edges
            for n in routing.nodes:
                for p in n.preds:
                    db.session.add(
                        OperationRoutingEdge(
                            routing_id=row.id,
                            from_node_id=key2id[p],
                            to_node_id=key2id[n.key],
                        )
                    )

            # 5) insertar steps
            for s in steps:
                db.session.add(
                    OperationRoutingStep(
                        routing_id=row.id,
                        sequence=s["sequence"],
                        node_id=key2id[s["node_key"]],
                        parallel_with_prev=bool(s["parallel_with_prev"]),
                    )
                )

            # 6) actualizar métricas de cabecera
            row.lt = metrics.lt
            row.bottleneck_node_key = metrics.bottleneck_key

        return {"ok": True, "model_id": dto.model_id, "id": row.id}

    @staticmethod
    def get(model_id: int) -> dict:
        row = db.session.query(OperationRouting).filter_by(model_id=model_id).first()
        if not row:
            raise NotFoundError("No hay routing para este modelo.")
        # reconstruye respuesta mínima (puedes enriquecer con joins)
        nodes_db = (
            db.session.query(OperationRoutingNode)
            .filter_by(routing_id=row.id)
            .order_by(OperationRoutingNode.level, OperationRoutingNode.id)
            .all()
        )
        edges_db = (
            db.session.query(OperationRoutingEdge).filter_by(routing_id=row.id).all()
        )

        # map id_db -> key lógico
        id2key = {n.id: n.node_key for n in nodes_db}

        # construir preds por key lógico
        preds_by_key = {n.node_key: [] for n in nodes_db}
        for e in edges_db:
            preds_by_key[id2key[e.to_node_id]].append(id2key[e.from_node_id])

        # levels a partir del campo "level" guardado
        max_level = max((n.level for n in nodes_db), default=0)
        levels = [
            [n.node_key for n in nodes_db if n.level == i] for i in range(max_level + 1)
        ]

        return {
            "id": row.id,
            "model_id": row.model_id,
            "lt": str(row.lt),
            "bottleneck_node_key": row.bottleneck_node_key,
            "nodes": [
                {
                    "id": n.node_key,
                    "operation_id": n.operation_id,
                    "ct": str(n.ct),
                    "es": str(n.es),
                    "ef": str(n.ef),
                    "ls": str(n.ls),
                    "lf": str(n.lf),
                    "slack": str(n.slack),
                    "crit": n.crit,
                    "level": n.level,
                    "preds": preds_by_key[n.node_key],  # 👈 clave
                }
                for n in nodes_db
            ],
            "levels": levels,  # 👈 opcional pero útil
            "edges_keys": [  # 👈 por si quieres depurar
                {"from": id2key[e.from_node_id], "to": id2key[e.to_node_id]}
                for e in edges_db
            ],
        }

    @staticmethod
    def delete(model_id: int) -> bool:
        row = db.session.query(OperationRouting).filter_by(model_id=model_id).first()
        if not row:
            raise NotFoundError("No hay routing para borrar.")
        db.session.delete(row)  # cascades borran nodos/edges/steps
        db.session.commit()
        return True
