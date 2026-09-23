# repositorio.py
# Este archivo concentra todas las consultas SQL del ejercicio.
# Todas usan parámetros ($1, $2, ...): nunca se concatenan valores
# recibidos del formulario dentro del texto SQL.


async def obtener_productos(conn) -> list[dict]:
    """Devuelve todos los productos, ordenados por nombre."""
    filas = await conn.fetch("SELECT * FROM productos ORDER BY nombre ASC;")
    return [dict(fila) for fila in filas]


async def obtener_producto(conn, producto_id: int) -> dict | None:
    """Busca un producto por su clave primaria (id)."""
    fila = await conn.fetchrow("SELECT * FROM productos WHERE id = $1;", producto_id)
    return dict(fila) if fila else None


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
        SET nombre = $1, precio = $2, cantidad = $3, descripcion = $4
        WHERE id = $5;
        """,
        nombre, precio, cantidad, descripcion, producto_id
    )
    return resultado == "UPDATE 1"