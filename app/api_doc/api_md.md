# Documentación de API - Clientes (POST)

## Endpoint

**POST** `/api/v1/clients`

---

## Descripción
Crea un nuevo cliente en el sistema.

---

## Headers requeridos

```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

---

## Cuerpo de la solicitud (JSON)

```json
{
  "ruc_or_ci": "0912345678",
  "name": "Zapatería El Paso",
  "client_type": "Mayorista",
  "address": "Av. Siempre Viva 123",
  "email": "contacto@elpaso.com",
  "province_id": 10,
  "canton_id": 105,
  "phone": "0987654321"
}
```

---

## Campos obligatorios
- `ruc_or_ci`: Cédula o RUC del cliente. Debe contener 10 o 13 dígitos numéricos.
- `name`: Nombre o razón social del cliente. Longitud mínima: 3 caracteres.
- `client_type`: Tipo de cliente (por ejemplo: Minorista, Mayorista). Valor esperado: string.
- `address`: Dirección fiscal o principal del cliente.
- `email`: Correo electrónico de contacto. Debe tener formato válido.
- `province_id`: ID de la provincia. Debe ser número entero.
- `canton_id`: ID del cantón asociado. Debe ser número entero.

**Nota**: `phone` es opcional, pero si se envía debe contener solo dígitos.

---

## Respuestas

### ✅ 201 - Cliente creado exitosamente

```json
{
  "message": "Cliente creado exitosamente",
  "client": {
    "id": 1,
    "ruc_or_ci": "0912345678",
    "name": "Zapatería El Paso",
    "client_type": "Mayorista",
    "address": "Av. Siempre Viva 123",
    "email": "contacto@elpaso.com",
    "province_id": 10,
    "canton_id": 105,
    "phone": "0987654321"
  }
}
```

### ⚠️ 400 - Faltan campos requeridos o validación fallida

```json
{
  "message": "Campo 'name' es requerido"
}

{
  "message": "El campo 'province_id' debe ser un número entero válido."
}

{
  "message": "El campo 'email' no es válido."
}
```

### ❌ 500 - Error interno inesperado

```json
{
  "message": "Error inesperado: <detalle_del_error>"
}
```

---

## Notas adicionales
- Este endpoint requiere autenticación JWT.
- El campo `canton_id` es validado para pertenecer a la provincia enviada (`province_id`).
- Validaciones de tipo y formato están incluidas en el backend.
- Se recomienda validar los datos desde el frontend antes de enviar la solicitud.
