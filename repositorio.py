# Este archivo concentra todas las consultas SQL del ejercicio.
# Todas usan parámetros ($1, $2, ...): nunca se concatenan valores
# recibidos del formulario dentro del texto SQL.
#
# Las cuatro operaciones siguen el mismo camino:
#   interfaz (HTMX) -> ruta de FastAPI (vistas.py) -> función de este archivo
#   -> consulta SQL -> PostgreSQL.


async def obtener_productos(conn) -> list[dict]:
    """Devuelve todos los productos, ordenados por nombre."""
    filas = await conn.fetch(
        """
        SELECT id, nombre, precio, cantidad, descripcion
          FROM productos
         ORDER BY nombre
        """
    )
    # asyncpg devuelve objetos Record; los pasamos a dict para que Jinja2
    # pueda leerlos con producto.nombre, producto.precio, etc.
    return [dict(fila) for fila in filas]


async def obtener_producto(conn, producto_id: int) -> dict | None:
    """Busca un producto por su clave primaria (id)."""
    fila = await conn.fetchrow(
        """
        SELECT id, nombre, precio, cantidad, descripcion
          FROM productos
         WHERE id = $1
        """,
        producto_id,
    )
    # fetchrow devuelve None cuando no hay ninguna fila con ese id.
    return dict(fila) if fila is not None else None


async def actualizar_producto(
    conn,
    producto_id: int,
    nombre: str,
    precio: float,
    cantidad: int,
    descripcion: str | None,
) -> bool:
    """Actualiza un producto identificado por su clave primaria (id).

    Devuelve True si la consulta modificó una fila, False si no existía.
    """
    resultado = await conn.execute(
        """
        UPDATE productos
           SET nombre = $2, precio = $3, cantidad = $4, descripcion = $5
         WHERE id = $1
        """,
        producto_id,
        nombre,
        precio,
        cantidad,
        descripcion,
    )
    # asyncpg devuelve la cadena "UPDATE 1" si modificó una fila
    # (y "UPDATE 0" si el id no existía).
    return resultado == "UPDATE 1"


async def eliminar_producto(conn, producto_id: int) -> bool:
    """Elimina un producto identificado por su clave primaria (id).

    Devuelve True si la consulta borró una fila, False si no existía.
    """
    resultado = await conn.execute(
        """
        DELETE FROM productos
         WHERE id = $1
        """,
        producto_id,
    )
    # Igual que en el UPDATE: "DELETE 1" significa que se borró una fila.
    # El WHERE con el id garantiza que solo se borra el producto elegido.
    return resultado == "DELETE 1"