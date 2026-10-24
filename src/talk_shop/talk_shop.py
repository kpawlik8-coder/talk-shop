"""Command-line shop assistant using a grammar supplied by the user."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Token, Tree
from lark.exceptions import LarkError, UnexpectedInput


@dataclass
class Product:
    name: str
    price: float
    stock: int


products: dict[str, Product] = {
    "monorail": Product(name="Monorail", price=1449.99, stock=30),
    "hewlett_packard": Product(name="Hewlett Packard", price=1849.99, stock=23),
    "compaq": Product(name="COMPAQ", price=2399.99, stock=8),
}


def load_parser(grammar_path: str) -> Lark:
    grammar = Path(grammar_path).read_text(encoding="utf-8")
    parser = Lark(grammar, parser="earley")
    return parser


def process_query(query: str, parser: Lark) -> str:
    try:
        query = query.strip().lower().rstrip("?!.")
        tree = parser.parse(query)
        query_node = tree.children[0]

        if not isinstance(query_node, Tree):
            return "Unable to process query."

        item = None

        for child in query_node.children:
            if isinstance(child, Token) and child.type == "ITEM":
                item = str(child)
                break

        if item is None:
            return "Unable to find the product name in the question."

        item = item.replace(" ", "_")
        product = products.get(item)

        if product is None:
            return f"Unknown product: {item}."

        if query_node.data == "price_question":
            return f"The {product.name} costs {product.price:.2f}$."

        if query_node.data == "availability_question":
            if product.stock > 0:
                return f"Yes, {product.name} is in stock."
            return f"No, {product.name} is out of stock."

        if query_node.data == "quantity_question":
            return f"There are {product.stock} units of {product.name} in stock."

        return "Unsupported question type."

    except UnexpectedInput:
        return (
            "I could not understand the question. "
            "Try: how much is compaq, is compaq in stock, "
            "or how many compaq do you have."
        )
    except Exception as error:
        return f"Unable to process the question: {error}"



def main() -> None:
    arguments = argparse.ArgumentParser(
        description="Ask about product prices and stock."
    )
    arguments.add_argument(
        "-g",
        "--grammar",
        required=True,
        help="Path to the grammar file",
    )
    options = arguments.parse_args()

    try:
        parser = load_parser(options.grammar)
    except (OSError, UnicodeError) as error:
        print(f"Unable to read the grammar file: {error}")
        return
    except LarkError as error:
        print(f"Invalid grammar: {error}")
        return
    except Exception as error:
        print(f"Unable to start the program: {error}")
        return

    print("Ask about a product's price, availability or quantity.")
    print("Type END to exit.")

    while True:
        try:
            query = input("Query: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if query.strip().upper() == "END":
            print("Goodbye!")
            return

        response = process_query(query, parser)
        print(response)
        

if __name__ == "__main__":
    main()
