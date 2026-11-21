"""Add, find, update and delete products in the database."""

import math

from sqlalchemy import delete, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from talk_shop.models.product import Product, ProductModel


def normalize_name(name: str) -> str:
    """Normalize spaces and underscores in a product name."""
    return " ".join(name.replace("_", " ").split())


def validate_product(product: Product) -> Product:
    """Check product data and return a normalized copy."""
    name = normalize_name(product.name)

    if not name or len(name) > 100:
        raise ValueError("The name must contain between 1 and 100 characters.")

    if not all(word.isascii() and word.isalpha() for word in name.split()):
        raise ValueError("Use English letters and spaces in the product name.")

    if not math.isfinite(product.price) or product.price < 0:
        raise ValueError("The price must be a finite number of zero or more.")

    if not isinstance(product.stock, int) or product.stock < 0:
        raise ValueError("Stock must be a whole number of zero or more.")

    return Product(name=name, price=product.price, stock=product.stock)


def find_model(name: str, session: Session) -> ProductModel | None:
    """Find a database record by its normalized name."""
    query = select(ProductModel).where(
        func.lower(ProductModel.name) == normalize_name(name).lower()
    )
    return session.scalars(query).first()


def add_product(product: Product, engine: Engine) -> None:
    """Validate and save a new product."""
    product = validate_product(product)

    with Session(engine) as session:
        if find_model(product.name, session) is not None:
            raise ValueError("A product with this name already exists.")

        session.add(
            ProductModel(
                name=product.name,
                price=product.price,
                stock=product.stock,
            )
        )
        session.commit()


def find_product(name: str, engine: Engine) -> Product | None:
    """Return product data or None when the product is missing."""
    with Session(engine) as session:
        model = find_model(name, session)

        if model is None:
            return None

        return Product(
            name=model.name,
            price=model.price,
            stock=model.stock,
        )


def list_products(engine: Engine) -> list[Product]:
    """Return all products ordered by name."""
    with Session(engine) as session:
        query = select(ProductModel).order_by(ProductModel.name)
        models = session.scalars(query).all()

        return [
            Product(name=model.name, price=model.price, stock=model.stock)
            for model in models
        ]


def update_product(
    name: str,
    updated_product: Product,
    engine: Engine,
) -> bool:
    """Update a product and report whether it was found."""
    updated_product = validate_product(updated_product)

    with Session(engine) as session:
        model = find_model(name, session)

        if model is None:
            return False

        duplicate = find_model(updated_product.name, session)

        if duplicate is not None and duplicate.id != model.id:
            raise ValueError("A product with this name already exists.")

        model.name = updated_product.name
        model.price = updated_product.price
        model.stock = updated_product.stock
        session.commit()

    return True


def delete_product(name: str, engine: Engine) -> bool:
    """Delete a product and report whether it was found."""
    with Session(engine) as session:
        model = find_model(name, session)

        if model is None:
            return False

        session.delete(model)
        session.commit()

    return True


def clear_db(engine: Engine) -> None:
    """Delete all products without removing the table."""
    with Session(engine) as session:
        session.execute(delete(ProductModel))
        session.commit()
