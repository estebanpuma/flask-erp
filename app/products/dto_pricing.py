from ..common.parsers import parse_bool, parse_date, parse_ids_list, parse_int, parse_str, parse_float, parse_srt_list

class PricingRequestDTO:
    '''DTO validador para producto'''
    def __init__(self, data: dict):
        self.name = parse_str(data.get("name"), field="Nombre")
        self.description = parse_str(data.get('description'), field='Descripcion', nullable=True)
        self.line_id = parse_int(data.get("line_id"), field="Linea")
        self.subline_id = parse_int(data.get("sub_line_id"), field="Sublinea", nullable=True)
        self.target_id = parse_int(data.get("target_id"), field="target")
        self.collection_id = parse_int(data.get("collection_id"), field="Coleccion")

