# domain/routing.py
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from typing import Dict, List, Optional

# precisión global sugerida (minutos con 3-4 decimales)
getcontext().prec = 28  # alta precisión interna


@dataclass
class RoutingNode:
    key: str  # id lógico del nodo (p.ej. "n1")
    operation_id: int
    ct: Decimal  # cycle time (min)
    preds: List[str] = field(default_factory=list)

    # métricas calculadas:
    es: Decimal = Decimal("0")
    ef: Decimal = Decimal("0")
    ls: Decimal = Decimal("0")
    lf: Decimal = Decimal("0")
    slack: Decimal = Decimal("0")
    crit: bool = False
    level: int = 0  # nivel por ES para layout


@dataclass
class RoutingMetrics:
    lt: Decimal
    bottleneck_key: Optional[str]
    levels: List[List[str]]  # lista de listas de node.key


@dataclass
class Routing:
    model_id: int
    nodes: List[RoutingNode]

    def compute(self) -> RoutingMetrics:
        # --- índice por id lógico ---
        by_id: Dict[str, RoutingNode] = {n.key: n for n in self.nodes}

        # --- indegree y sucesores ---
        indeg: Dict[str, int] = {n.key: 0 for n in self.nodes}
        succ: Dict[str, List[str]] = {n.key: [] for n in self.nodes}
        for n in self.nodes:
            for p in n.preds:
                indeg[n.key] += 1
                succ.setdefault(p, []).append(n.key)

        # --- Kahn (orden topológico) ---
        q: List[str] = [k for k, d in indeg.items() if d == 0]
        order: List[str] = []
        while q:
            u = q.pop(0)
            order.append(u)
            for v in succ.get(u, []):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != len(self.nodes):
            raise ValueError("Se detectó un ciclo en predecesores.")

        # --- Forward (ES/EF) ---
        for nid in order:
            n = by_id[nid]
            if n.preds:
                n.es = max(by_id[p].ef for p in n.preds)
            else:
                n.es = Decimal("0")
            n.ef = n.es + n.ct

        lt = max((n.ef for n in self.nodes), default=Decimal("0"))

        # --- Backward (LS/LF) ---
        LS: Dict[str, Decimal] = {}
        LF: Dict[str, Decimal] = {}
        for nid in reversed(order):
            n = by_id[nid]
            children = succ.get(nid, [])
            LF[nid] = min((LS[c] for c in children), default=lt)
            LS[nid] = LF[nid] - n.ct
            n.ls, n.lf = LS[nid], LF[nid]

        # --- Slack / críticos ---
        for n in self.nodes:
            n.slack = n.ls - n.es
            n.crit = n.slack.copy_abs() <= Decimal("0.0000001")

        # --- Cuello de botella: crítico con mayor CT ---
        crits = [n for n in self.nodes if n.crit]
        bottleneck_key = None
        if crits:
            max_ct = max(n.ct for n in crits)
            bottleneck_key = next(n.key for n in crits if n.ct == max_ct)

        # --- Levels por ES (con redondeo estable para agrupar) ---
        # Nota: no flotantes. Usamos cuantización opcional si quieres bucketizar.
        # Aquí solo ordenamos por ES y asignamos índice incremental.
        unique_sorted_es = sorted({n.es for n in self.nodes})
        es_to_level = {es: i for i, es in enumerate(unique_sorted_es)}
        for n in self.nodes:
            n.level = es_to_level[n.es]

        levels: List[List[str]] = []
        max_level = max((n.level for n in self.nodes), default=0)
        for lvl in range(0, max_level + 1):
            levels.append([n.key for n in self.nodes if n.level == lvl])

        return RoutingMetrics(lt=lt, bottleneck_key=bottleneck_key, levels=levels)

    def to_linear_steps(self) -> List[dict]:
        """Deriva pasos lineales desde levels; marca paralelos dentro del mismo nivel."""
        metrics = self.compute()  # asegura levels actualizados
        # orden interno estable por key; ajusta si prefieres por nombre/CT
        seq, steps = 1, []
        by_id = {n.key: n for n in self.nodes}
        for lvl in metrics.levels:
            for i, key in enumerate(sorted(lvl)):
                n = by_id[key]
                steps.append(
                    {
                        "sequence": seq,
                        "node_key": n.key,
                        "operation_id": n.operation_id,
                        "ct_minutes": str(n.ct),  # ojo: Decimal → str si devuelves JSON
                        "parallel_with_prev": i > 0,
                    }
                )
                seq += 1
        return steps

    @staticmethod
    def from_dto(model_id: int, dto_nodes: List[dict]) -> "Routing":
        """Creador práctico desde DTOs Pydantic o dicts validados."""

        def D(x):
            return x if isinstance(x, Decimal) else Decimal(str(x))

        nodes = [
            RoutingNode(
                key=str(n["id"]),
                operation_id=int(n["operation_id"]),
                ct=D(n["ct"]),
                preds=[str(p) for p in (n.get("preds") or [])],
            )
            for n in dto_nodes
        ]
        return Routing(model_id=model_id, nodes=nodes)
