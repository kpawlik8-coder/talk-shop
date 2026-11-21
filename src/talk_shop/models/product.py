"""Define the product data and database table."""

from dataclasses import dataclass

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


@dataclass
class Product:
    """Represent product data used by the application."""

    name: str
    price: float
    stock: int


class DatabaseModel(DeclarativeBase):
    """Provide the base class for database models."""


class ProductModel(DatabaseModel):
    """Store a product's identifier, name, price and stock."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float())
    stock: Mapped[int] = mapped_column(Integer())
