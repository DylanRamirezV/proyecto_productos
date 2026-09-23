# Ejercicio: edición de productos

## 1. Contexto

La tienda "TechStore" guarda su catálogo en una tabla `productos` de una base de
datos PostgreSQL. El equipo de desarrollo ya construyó una aplicación web con
**FastAPI** que muestra la lista de productos en una tabla HTML, y utiliza
**HTMX** para actualizar partes de la página sin recargarla por completo.

Tu misión es completar la funcionalidad que permite **editar un producto
existente**: seleccionarlo, cargar sus datos actuales en un formulario,
validar los cambios y guardarlos en la base de datos.

Editar registros es una de las operaciones fundamentales de cualquier
aplicación con base de datos (el clásico CRUD: *Create, Read, **Update**,
Delete*). En este ejercicio te centrarás en la "U" de *Update*.

## 2. Objetivo de aprendizaje

Al terminar este ejercicio serás capaz de:

1. Cargar los datos actuales de un registro en un formulario HTML.
2. Recibir y validar los datos enviados por el usuario antes de modificar nada.
3. Ejecutar una consulta `UPDATE` segura, identificando el registro por su
   clave primaria.
4. Actualizar la interfaz con HTMX usando la respuesta HTML del servidor,
   sin recargar la página.
5. Conservar los valores ingresados y mostrar mensajes claros cuando la
   validación falla.

## 3. Descripción del problema

La aplicación ya funciona así:

- `GET /productos` consulta la tabla `productos` y muestra el catálogo en
  `<http://127.0.0.1:8000/productos>`.
- Cada fila de la tabla es un `<tbody>` con `id="producto-<id>"`, seguido de un
  botón **Editar** con atributos HTMX ya configurados:

  ```html
  <button
      hx-get="/productos/5/editar"
      hx-target="#producto-5"
      hx-swap="outerHTML">
      Editar
  </button>
  ```

  Al pulsarlo, HTMX hace `GET /productos/5/editar` y **reemplaza** ese
  `<tbody>` con la respuesta HTML del servidor.

Falta que implementes las tres rutas de edición:

| Ruta                          | Qué debe hacer                                                               |
| ----------------------------- | ---------------------------------------------------------------------------- |
| `GET /productos/{id}/editar`  | Buscar el producto y responder con el formulario (plantilla `fila_editar.html`) |
| `POST /productos/{id}`       | Validar los datos y, si son correctos, ejecutar el `UPDATE`                   |
| `GET /productos/{id}/cancelar` | Ya está implementada: devuelve la fila a su estado normal                   |

El formulario dentro de `fila_editar.html` ya envía los datos con HTMX:

```html
<form
    hx-post="/productos/5"
    hx-target="#producto-5"
    hx-swap="outerHTML">
```

El servidor debe responder con uno de estos fragmentos HTML, según el caso:

- `componentes/fila_editar.html` → si hay errores de validación (código 422).
- `componentes/fila_actualizada.html` → si el `UPDATE` se ejecutó con éxito.
- `componentes/producto_no_encontrado.html` → si el `id` no existe en la tabla.

Las plantillas ya existen: solo debes pasarles los datos correctos.

## 4. Tecnologías y dependencias

Instala las dependencias del proyecto (ya listadas en `requirements.txt`):

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Esto instala:

- `fastapi[standard]`: FastAPI junto con Uvicorn (el servidor de desarrollo).
- `asyncpg`: cliente asíncrono para PostgreSQL.

Jinja2 viene incluido con FastAPI (lo usamos mediante
`fastapi.templating.Jinja2Templates`). HTMX se carga desde una etiqueta
`<script>` en `templates/base.html`; no necesitas instalar nada más.

## 5. Base de datos y tabla

La cadena de conexión se lee de la variable de entorno `DATABASE_URL` (ver
`.env.example`). Crea un archivo `.env` con el valor que te proporcione el
docente y expórtalo antes de arrancar el servidor:

```bash
export DATABASE_URL="postgresql://usuario:contrasena@host:puerto/basedatos"
```

La tabla `productos` ya existe en la base de datos y tiene esta estructura:

| Campo         | Tipo      | Nulo | Descripción              |
| ------------- | --------- | ---- | ------------------------ |
| `id`          | `INTEGER` | no   | Clave primaria (serie)   |
| `nombre`      | `VARCHAR` | no   | Nombre del producto      |
| `precio`      | `NUMERIC` | no   | Precio del producto      |
| `cantidad`    | `INTEGER` | no   | Cantidad disponible      |
| `descripcion` | `TEXT`    | sí   | Descripción del producto |

**Importante:** el `UPDATE` siempre debe identificar el registro por su clave
primaria `id`. Jamás construyas la consulta SQL concatenando texto: usa los
parámetros posicionales de asyncpg (`$1`, `$2`, ...).

## 6. Requisitos funcionales

Tu implementación debe cumplir lo siguiente:

1. Al pulsar **Editar**, la fila se convierte en un formulario con los
   **valores actuales** del producto.
2. Al pulsar **Guardar**, los datos se envían al servidor y se validan:
   - `nombre` es obligatorio.
   - `precio` debe ser un número mayor que cero.
   - `cantidad` debe ser un número entero mayor o igual que cero.
   - `descripcion` es opcional.
3. Si hay errores de validación:
   - **No se modifica la base de datos.**
   - El formulario se vuelve a mostrar **con los valores que el usuario
     escribió** (no con los originales).
   - Cada campo con error muestra un mensaje comprensible.
4. Si los datos son válidos:
   - Se ejecuta un `UPDATE` **solo sobre el registro con ese `id`**.
   - La fila de la tabla muestra los nuevos valores.
   - Aparece un aviso de "Producto actualizado correctamente".
5. Si el `id` no existe, se muestra un aviso en lugar de un error del servidor.
6. **Cancelar** devuelve la fila a su estado normal sin modificar nada
   (esta ruta ya está implementada).

## 7. Instrucciones de trabajo paso a paso

Abre cada archivo indicado y busca los comentarios `TODO(n)`. Trabajá en este
orden (cada paso depende del anterior):

**Paso 1 — Validación (`esquemas.py`)**

Define la clase `ProductoActualizar` con las reglas de validación del
requisito 2, usando los campos de Pydantic (`Field`).

**Paso 2 — Consultas (`repositorio.py`)**

Implementa las tres funciones (imítate la firma que ya está escrita):

- `obtener_productos(conn)`: `SELECT` de todos los productos.
- `obtener_producto(conn, producto_id)`: `SELECT` de un producto por su `id`.
- `actualizar_producto(...)`: `UPDATE ... WHERE id = $n` con parámetros.

Prueba que devuelven datos reales llamándolas desde `vistas.py`.

**Paso 3 — Formulario de edición (`vistas.py`, ruta `editar_producto_vista`)**

Completa `GET /productos/{producto_id}/editar`: busca el producto y renderiza
`componentes/fila_editar.html`. Comprueba en el navegador que el formulario
muestra los valores actuales del producto.

**Paso 4 — Guardar cambios (`vistas.py`, ruta `guardar_producto_vista`)**

Completa `POST /productos/{producto_id}`:

1. Convierte los valores de texto a número (`float` / `int`).
2. Valida con `ProductoActualizar`.
3. Si hay errores → renderiza el formulario de nuevo con los valores
   recibidos y un diccionario de errores, y responde con código 422.
4. Si es válido → ejecuta `actualizar_producto` y renderiza
   `componentes/fila_actualizada.html` con el producto actualizado.

**Paso 5 — Pruebas manuales**

Recorre la lista de comprobaciones de la sección siguiente.

### Sugerencias

- Ejecuta el servidor con `uvicorn main:app --reload` para que los cambios se
  recarguen solos.
- Fíjate cómo la ruta `cancelar_edicion_vista` usa `templates.TemplateResponse`:
  las demás rutas siguen el mismo patrón.
- Para el diccionario de errores puedes usar `{"nombre": "mensaje", ...}` y la
  plantilla lo mostrará debajo de cada campo con `errores.nombre`.
- Si una consulta asyncpg modifica una fila, `conn.execute(...)` devuelve la
  cadena `"UPDATE 1"`.
- Para depurar, mira la terminal donde corre Uvicorn y usa las herramientas de
  desarrollo del navegador (pestaña *Network*).

## 8. Criterios de aceptación

Marca cada casilla cuando lo compruebes:

- [ ] La lista de productos se muestra en `/productos`.
- [ ] Al pulsar **Editar**, el formulario aparece con los valores actuales del
      producto, sin recargar la página.
- [ ] Al pulsar **Cancelar**, la fila vuelve a su estado normal.
- [ ] Si envías el formulario vacío, aparecen mensajes de error y **los datos
      de la base de datos no cambian**.
- [ ] Si escribes un precio negativo o cero, aparece un mensaje de error.
- [ ] Si escribes una cantidad no numérica o negativa, aparece un mensaje de
      error y el valor escrito se conserva en el campo.
- [ ] Si envías datos válidos, la fila de la tabla muestra los nuevos valores
      y el aviso de éxito.
- [ ] Si editas el producto A, el producto B no cambia (el `UPDATE` afecta solo
      al registro indicado).
- [ ] La consulta `UPDATE` usa parámetros `$1, $2, ...` (sin concatenar texto).
- [ ] Al abrir `/productos/99999/editar` se muestra el aviso de "no
      encontrado" en lugar de un error 500.

## 9. Cómo ejecutar y probar

```bash
# 1. Entorno virtual (si no lo creaste antes)
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar la conexión (una sola línea)
export DATABASE_URL="postgresql://usuario:contrasena@host:puerto/basedatos"

# 3. Arrancar el servidor de desarrollo
uvicorn main:app --reload
```

Abre <http://127.0.0.1:8000/productos> en tu navegador y prueba el flujo
completo: editar → validar errores → corregir → guardar → verificar la fila
actualizada.

También puedes probar las rutas directamente con `curl`:

```bash
# Formulario de edición del producto con id 3
curl http://127.0.0.1:8000/productos/3/editar

# Guardar cambios válidos
curl -X POST http://127.0.0.1:8000/productos/3 \
  -d "nombre=Producto de prueba" -d "precio=19.99" \
  -d "cantidad=5" -d "descripcion=Una descripción"
```

> Nota: el comando `curl` no ejecuta HTMX, así que verás el fragmento HTML de
> respuesta, pero es una forma rápida de comprobar que el servidor responde
> bien. Prueba siempre también desde el navegador.

¡Mucho éxito! Cuando termines, compara tu solución con la carpeta `solucion/`
que incluye el docente.