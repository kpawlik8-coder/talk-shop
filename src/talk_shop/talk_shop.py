"""Command-line shop assistant using a grammar supplied by the user."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Token, Tree
from lark.exceptions import LarkError, UnexpectedInput


@dataclass
class Product:
    """Store a product's name, price and available quantity."""

    name: str
    price: float
    stock: int


products: dict[str, Product] = {
    "monorail": Product(name="Monorail", price=1449.99, stock=30),
    "hewlett_packard": Product(name="Hewlett Packard", price=1849.99, stock=23),
    "compaq": Product(name="COMPAQ", price=2399.99, stock=8),
}


def load_parser(grammar_path: str) -> Lark:
    """Read the grammar file and create a parser."""
    grammar = Path(grammar_path).read_text(encoding="utf-8")
    parser = Lark(grammar, parser="earley")
    return parser


def find_product(question: Tree) -> Product | None:
    """Find the product mentioned in the question."""
    for child in question.children:
        if isinstance(child, Token) and child.type == "ITEM":
            item = str(child).replace(" ", "_")
            return products.get(item)

    return None


def answer_question(question_type: str, product: Product) -> str:
    """Prepare an answer about the selected product."""
    if question_type == "price_question":
        return f"The {product.name} costs {product.price:.2f}$."

    if question_type == "availability_question":
        if product.stock > 0:
            response = f"Yes, {product.name} is in stock."
        else:
            response = f"No, {product.name} is out of stock."
        return response

    if question_type == "quantity_question":
        return f"There are {product.stock} units of {product.name} in stock."

    return "I cannot answer this question. Please write END to finish."


def process_query(query: str, parser: Lark) -> str:
    """Recognize a question and return a response to the user."""
    try:
        query = query.strip().lower().rstrip("?!.").strip()
        tree = parser.parse(query)
        question = tree.children[0]

        if not isinstance(question, Tree):
            response = (
                "I could not understand the question.\n"
                "Try: how much is compaq.\n"
                "Please write END to finish the conversation."
            )
        else:
            product = find_product(question)

            if product is None:
                response = (
                    "I could not find that product in our shop.\n"
                    "Try asking about monorail, compaq or hewlett_packard.\n"
                    "Please write END to finish the conversation."
                )
            else:
                response = answer_question(str(question.data), product)

    except UnexpectedInput:
        response = (
            "I could not understand the question.\n"
            "Try: how much is compaq, is compaq in stock, "
            "or how many compaq do you have.\n"
            "Please write END to finish the conversation."
        )
    except Exception:
        response = (
            "Sorry, I could not answer your question. Please try again.\n"
            "Please write END to finish the conversation."
        )

    return response


def run_conversation(parser: Lark) -> None:
    """Ask for questions until the user ends the conversation."""
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


def main() -> None:
    """Read command-line arguments and start the shop assistant."""
    arguments = argparse.ArgumentParser(description=__doc__)
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

    run_conversation(parser)


if __name__ == "__main__":
    main()