from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from dependencias import ConnectionDep
from esquemas import ProductoActualizar
from repositorio import actualizar_producto, obtener_producto, obtener_productos

router = APIRouter(tags=["productos"])

templates = Jinja2Templates(directory="templates")


@router.get("/productos")
async def listar_productos(request: Request, conn: ConnectionDep):
    productos = await obtener_productos(conn)
    return templates.TemplateResponse(
        request=request,
        name="productos.html",
        context={"productos": productos},
    )


@router.get("/productos/{producto_id}/editar")
async def editar_producto_vista(request: Request, conn: ConnectionDep, producto_id: int):
    producto = await obtener_producto(conn, producto_id)
    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_editar.html",
        context={
            "producto": producto,
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": producto["cantidad"],
            "descripcion": producto["descripcion"],
            "errores": {},
        },
    )


@router.get("/productos/{producto_id}/cancelar")
async def cancelar_edicion_vista(request: Request, conn: ConnectionDep, producto_id: int):
    producto = await obtener_producto(conn, producto_id)
    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )
    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_producto.html",
        context={"producto": producto},
    )


@router.post("/productos/{producto_id}")
async def guardar_producto_vista(
    request: Request,
    conn: ConnectionDep,
    producto_id: int,
    nombre: Annotated[str | None, Form()] = None,
    precio: Annotated[str | None, Form()] = None,
    cantidad: Annotated[str | None, Form()] = None,
    descripcion: Annotated[str | None, Form()] = None,
):
    producto = await obtener_producto(conn, producto_id)
    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    errores = {}

    # 1. Transformación previa: parsear datos numéricos desde texto
    precio_convertido = None
    if precio is not None and precio.strip() != "":
        try:
            precio_convertido = float(precio)
        except ValueError:
            errores["precio"] = "El precio debe ser un número válido."

    cantidad_convertida = None
    if cantidad is not None and cantidad.strip() != "":
        try:
            cantidad_convertida = int(cantidad)
        except ValueError:
            errores["cantidad"] = "La cantidad debe ser un número entero."

    datos_validados = None

    # 2. Validar con Pydantic si las conversiones previas no fallaron
    if not errores:
        datos_dict = {
            "nombre": nombre.strip() if nombre else None,
            "precio": precio_convertido,
            "cantidad": cantidad_convertida,
            "descripcion": descripcion.strip() if descripcion else None,
        }

        try:
            datos_validados = ProductoActualizar(**datos_dict)
        except ValidationError as e:
            for err in e.errors():
                campo = str(err["loc"][0])
                errores[campo] = err["msg"]

    # 3. Si hay errores (conversión o Pydantic), devolver la plantilla con estado 422
    if errores:
        return templates.TemplateResponse(
            request=request,
            name="componentes/fila_editar.html",
            context={
                "producto": producto,
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "descripcion": descripcion,
                "errores": errores,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # 4. Si todo es válido, actualizar base de datos
    await actualizar_producto(
        conn,
        producto_id=producto_id,
        nombre=datos_validados.nombre,
        precio=datos_validados.precio,
        cantidad=datos_validados.cantidad,
        descripcion=datos_validados.descripcion,
    )

    producto_actualizado = await obtener_producto(conn, producto_id)

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_actualizada.html",
        context={"producto": producto_actualizado},
    )