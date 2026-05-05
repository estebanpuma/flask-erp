# Flask ERP

Aplicación ERP modular construida con **Flask**, **Flask-RESTful**, **SQLAlchemy** y una capa web server-rendered (Jinja + JS estático).

## 1) ¿Qué hace esta app?

El proyecto centraliza procesos operativos y administrativos de una empresa manufacturera/comercial:

- Administración y autenticación de usuarios.
- CRM (clientes y contactos).
- Catálogo de productos, colecciones, tallas/series y medios asociados.
- Materiales, lotes, inventario y movimientos de stock.
- Ventas, pagos y finanzas.
- Producción y ruteo.
- Proveedores y módulos de soporte.

La app expone **API REST versionada** y además provee **vistas web** para operación interna.

---

## 2) Arquitectura actual (visión rápida)

### Stack principal
- **Backend:** Flask + Flask-RESTful.
- **Persistencia:** SQLAlchemy + Flask-Migrate (PostgreSQL por defecto).
- **Auth:** JWT (`flask_jwt_extended`).
- **Frontend:** plantillas Jinja en `app/web_app/templates` + JavaScript estático en `app/web_app/static/js`.
- **Media/Storage:** servicio local en `app/storage/local.py`.

### Patrón por módulos
La app está organizada por dominios (`app/<modulo>`). En la mayoría de módulos se repite este esquema:

- `models.py`: entidades ORM.
- `resources.py`: endpoints REST.
- `services.py`: lógica de negocio.
- `api.py`: blueprint + registro de recursos.
- `schemas.py` / `dto.py` / `entities.py`: serialización, contratos y lógica de dominio complementaria.

### Bootstrapping
`create_app` en `app/__init__.py`:
- Carga configuración.
- Inicializa extensiones (`db`, `migrate`, JWT, CORS, logging).
- Registra blueprints API y web.
- Crea carpetas de carga de archivos configuradas.

---

## 3) Estructura del repositorio

```text
app/
  __init__.py                 # factory principal
  admin/ auth/ core/ common/  # módulos base
  crm/ products/ materials/
  inventory/ sales/ payments/
  production/ suppliers/
  media/ finance/ pricing/
  web_app/                    # UI Jinja + JS
  storage/                    # servicios de almacenamiento
config/
  config.py                   # configuración global
run.py                        # entrada local
Dockerfile / docker-compose.yml
requirements.txt
```

---

## 4) Ejecución local

## Requisitos
- Python 3.10+ recomendado.
- PostgreSQL (o ajustar `DATABASE_URL`).

## Variables/ajustes clave
- `DATABASE_URL` (si no, usa la default de `config/config.py`).
- `SECRET_KEY` / `JWT_SECRET_KEY` (recomendado mover a entorno).

## Comandos sugeridos
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

La app quedará disponible en `http://localhost:5000`.

---

## 5) Endpoints y UI

- API versionada bajo `/api/v1` (con variaciones por módulo, por ejemplo `/api/v1/auth`, `/api/v1/media`).
- UI web mediante blueprints en `app/web_app/routes`.

---

## 6) Estado técnico observado

Fortalezas:
- Separación por dominio funcional clara.
- Existe capa de servicios en casi todos los módulos.
- Factory app + blueprints ya implementados.

Riesgos técnicos:
- Nomenclatura inconsistente (ej. `Secuence` vs `Sequence`).
- Manejo de errores heterogéneo (`except Exception` extendido).
- Múltiples `print()` de depuración en código de negocio.
- Configuración sensible hardcodeada en `config.py`.
- Archivos y nombres legacy/duplicados (ej. `dto copy.py`).

---

## 7) Ruta recomendada para continuar desarrollo

1. Estandarizar contratos API (payload, errores, paginación).
2. Consolidar capa de dominio/servicios por módulo.
3. Unificar logging y observabilidad.
4. Añadir tests (unitarios + integración de recursos críticos).
5. Endurecer configuración por ambiente (dev/staging/prod).

Ver documento complementario: **`REFACTORING_SUGERENCIAS.md`**.
