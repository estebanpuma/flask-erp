# 📚 Documentación de la API de Clientes

---

## ✨ Endpoints disponibles

| Método | Endpoint | Descripción |
|:---|:---|:---|
| `GET` | `/api/v1/clients` | Listar todos los clientes |
| `GET` | `/api/v1/clients/<client_id>` | Obtener un cliente por ID |
| `POST` | `/api/v1/clients` | Crear un nuevo cliente |
| `PATCH` | `/api/v1/clients/<client_id>` | Actualizar parcialmente un cliente |
| `DELETE` | `/api/v1/clients/<client_id>` | Eliminar un cliente |

---

## 📌 Headers requeridos

```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

---

## 📥 Crear un nuevo cliente

**POST** `/api/v1/clients`

### Cuerpo del Request:

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

- **Campos obligatorios**: `ruc_or_ci`, `name`, `client_type`, `address`, `email`, `province_id`, `canton_id`
- **Campo opcional**: `phone`

### Respuesta exitosa (201):

```json
{
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
```

---

## 📤 Obtener un cliente o listar clientes

**GET** `/api/v1/clients`  
**GET** `/api/v1/clients/<client_id>`

- Si se pasa `client_id`, retorna un cliente.
- Si no se pasa nada, retorna la lista de todos los clientes.

### Ejemplo de respuesta (200):

```json
[
  {
    "id": 1,
    "ruc_or_ci": "0912345678",
    "name": "Zapatería El Paso",
    "client_type": "Mayorista",
    "address": "Av. Siempre Viva 123",
    "email": "contacto@elpaso.com",
    "province_id": 10,
    "canton_id": 105,
    "phone": "0987654321"
  },
  ...
]
```

---

## 🔄 Actualizar parcialmente un cliente

**PATCH** `/api/v1/clients/<client_id>`

### Cuerpo del Request:

Puedes enviar **solo los campos que deseas actualizar**:

```json
{
  "address": "Nueva dirección actualizada",
  "phone": "0998765432"
}
```

### Respuesta exitosa (200):

```json
{
  "id": 1,
  "ruc_or_ci": "0912345678",
  "name": "Zapatería El Paso",
  "client_type": "Mayorista",
  "address": "Nueva dirección actualizada",
  "email": "contacto@elpaso.com",
  "province_id": 10,
  "canton_id": 105,
  "phone": "0998765432"
}
```

---

## ❌ Eliminar un cliente

**DELETE** `/api/v1/clients/<client_id>`

### Respuesta exitosa (200):

```json
{
  "message": "Recurso eliminado correctamente"
}
```

---

## ⚠️ Respuestas de error

| Código | Descripción |
|:---|:---|
| 400 | Datos inválidos o malformados |
| 401 | No autorizado (falta o error en el token) |
| 403 | Acceso denegado |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

---

# 🚀 ¡Con esto tienes la documentación lista y profesional! 

✨️ **Última actualización: 28 de Abril 2025**
