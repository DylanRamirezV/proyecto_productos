from pydantic import BaseModel, Field


class ProductoActualizar(BaseModel):
    """Datos que el estudiante envía al editar un producto.

    Pydantic revisa estos datos ANTES de tocar la base de datos: si algo
    no cumple las reglas, se lanza un error de validación y no se ejecuta
    ningún UPDATE.
    """

    # Obligatorio, entre 1 y 100 caracteres.
    nombre: str = Field(min_length=1, max_length=100)
    # Número mayor que cero (gt = "greater than").
    precio: float = Field(gt=0)
    # Número entero mayor o igual que cero (ge = "greater or equal").
    cantidad: int = Field(ge=0)
    # Opcional: puede venir vacío o no venir.
    descripcion: str | None = None