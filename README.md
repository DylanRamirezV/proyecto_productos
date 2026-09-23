# Ejercicio: edición de productos (proyecto base)

Proyecto de partida del ejercicio **"Edición de registros con FastAPI, Jinja2, HTMX y PostgreSQL"**.

El enunciado completo está en [`Docs/ejercicio_edicion_productos.md`](Docs/ejercicio_edicion_productos.md).

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

Edita `.env` y define la cadena de conexión a tu base de datos PostgreSQL.

## Ejecución

```bash
uvicorn main:app --reload
```

Abre el navegador en <http://127.0.0.1:8000/productos>.

## Estado del proyecto

- La página `GET /productos` ya muestra la lista de productos.
- El botón **Editar** apunta a las rutas que debes implementar.
- Los archivos `esquemas.py`, `repositorio.py` y `vistas.py` contienen
  comentarios `TODO(n)` que indican qué falta en cada paso.
- La carpeta `solucion/` contiene la implementación completa de referencia.