from ..common.parsers import (
    parse_int, parse_float, parse_date, parse_str
)



class PAymentMethodEntity():
    def __init__(self, data: dict):
        self.name = parse_str(data.get('name'), field='name')
        self.description = parse_str(data.get('description'), field='description')



