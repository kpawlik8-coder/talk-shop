"""Provide a command-line menu for managing shop products."""

from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from talk_shop.core.products import (
    add_product,
    clear_db,
    delete_product,
    find_product,
    list_products,
    update_product,
)
from talk_shop.models.product import Product


def read_product() -> Product:
    """Read product details from the administrator."""
    name = input("Product name: ").strip()

    try:
        price = float(input("Price: ").strip().replace(",", "."))
        stock = int(input("Stock: ").strip())
    except ValueError as error:
        raise ValueError(
            "Enter a numeric price and a whole number for stock."
        ) from error

    return Product(name=name, price=price, stock=stock)


def show_product(product: Product) -> None:
    """Display a product's details."""
    print(f"{product.name} | Price: {product.price:.2f}$ | Stock: {product.stock}")


def add_action(engine: Engine) -> None:
    """Add a new product."""
    product = read_product()
    add_product(product, engine)
    print("Product added.")


def find_action(engine: Engine) -> None:
    """Find and display a product."""
    product = find_product(input("Product name: "), engine)

    if product is None:
        print("Product not found.")
        return

    show_product(product)


def update_action(engine: Engine) -> None:
    """Change an existing product."""
    name = input("Name of the product to change: ")
    product = find_product(name, engine)

    if product is None:
        print("Product not found.")
        return

    print("Current details:")
    show_product(product)
    print("Enter all new details, including the name.")
    updated_product = read_product()

    if update_product(name, updated_product, engine):
        print("Product updated.")
    else:
        print("Product not found.")


def delete_action(engine: Engine) -> None:
    """Delete a product after confirmation."""
    name = input("Name of the product to delete: ")
    product = find_product(name, engine)

    if product is None:
        print("Product not found.")
        return

    show_product(product)
    confirmation = input("Type YES to delete this product: ")

    if confirmation.strip().upper() != "YES":
        print("Deletion cancelled.")
        return

    if delete_product(name, engine):
        print("Product deleted.")
    else:
        print("Product not found.")


def list_action(engine: Engine) -> None:
    """Display all products."""
    products = list_products(engine)

    if not products:
        print("The shop has no products.")
        return

    for product in products:
        show_product(product)


def clear_action(engine: Engine) -> None:
    """Delete all products after confirmation."""
    confirmation = input("This will delete ALL products. Type CLEAR to confirm: ")

    if confirmation.strip().upper() != "CLEAR":
        print("Clearing cancelled.")
        return

    clear_db(engine)
    print("All products deleted.")


def print_menu() -> None:
    """Display the administrator menu."""
    print(
        "\nADMIN MENU\n"
        "1 - Add product\n"
        "2 - Find product\n"
        "3 - Change product\n"
        "4 - Delete product\n"
        "5 - List products\n"
        "6 - Clear database\n"
        "0 - Exit"
    )


def run_admin(engine: Engine) -> None:
    """Run administrator actions until the user exits."""
    actions = {
        "1": add_action,
        "2": find_action,
        "3": update_action,
        "4": delete_action,
        "5": list_action,
        "6": clear_action,
    }

    while True:
        try:
            print_menu()
            choice = input("Choose an option: ").strip()

            if choice.upper() in ("0", "END"):
                print("Goodbye!")
                return

            action = actions.get(choice)

            if action is None:
                print("Choose a number from 1 to 6, or 0 to exit.")
            else:
                action(engine)

        except ValueError as error:
            print(error)
            print("Please try again. Choose 0 to exit.")
        except SQLAlchemyError:
            print(
                "The database operation could not be completed. "
                "Please try again. Choose 0 to exit."
            )
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
