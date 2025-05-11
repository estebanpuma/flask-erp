## Guía de excepciones por módulo

### General
- ValidationError → cuando los datos están mal (campos vacíos, tipo incorrecto)
- ConflictError → cuando algo ya existe
- NotFoundError → cuando no se encuentra un ID o entidad

### Uso típico en services:
- raise ConflictError("Ya existe un cliente con ese email.")
- raise NotFoundError("No se encontró el pedido con ID 43.")
