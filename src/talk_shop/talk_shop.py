"""Run the shop chatbot or the administrator menu."""

import argparse
from pathlib import Path

from lark import Lark, Token, Tree
from lark.exceptions import LarkError, UnexpectedInput
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from talk_shop.core.database import prepare_db
from talk_shop.core.products import find_product as find_product_in_db
from talk_shop.models.product import Product
from talk_shop.services.admin import run_admin


def load_parser(grammar_path: str) -> Lark:
    """Read the grammar file and create a parser."""
    grammar = Path(grammar_path).read_text(encoding="utf-8")
    return Lark(grammar, parser="earley")


def find_product(question: Tree, engine: Engine) -> Product | None:
    """Find the product mentioned in a question."""
    for child in question.children:
        if isinstance(child, Token) and child.type == "ITEM":
            name = str(child).replace("_", " ")
            return find_product_in_db(name, engine)

    return None


def answer_question(question_type: str, product: Product) -> str:
    """Prepare an answer about a product."""
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


def process_query(query: str, parser: Lark, engine: Engine) -> str:
    """Recognize a question and answer using database data."""
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
            product = find_product(question, engine)

            if product is None:
                response = (
                    "I could not find that product in our shop.\n"
                    "Please check the product name and try again.\n"
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
    except SQLAlchemyError:
        response = (
            "Product information is temporarily unavailable.\n"
            "Please try again or write END to finish."
        )
    except Exception:
        response = (
            "Sorry, I could not answer your question.\n"
            "Please try again or write END to finish."
        )

    return response


def run_conversation(parser: Lark, engine: Engine) -> None:
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

        print(process_query(query, parser, engine))


def read_arguments() -> argparse.Namespace:
    """Read options and require a grammar only for the chatbot."""
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument(
        "--admin",
        action="store_true",
        help="Open the administrator menu",
    )
    arguments.add_argument(
        "-g",
        "--grammar",
        help="Path to the grammar file; required for the chatbot",
    )
    options = arguments.parse_args()

    if not options.admin and not options.grammar:
        arguments.error("the chatbot requires -g or --grammar")

    return options


def run_application(options: argparse.Namespace) -> None:
    """Prepare resources and run the selected application mode."""
    parser = None

    if not options.admin:
        parser = load_parser(options.grammar)

    engine = prepare_db()

    try:
        if options.admin:
            run_admin(engine)
        elif parser is not None:
            run_conversation(parser, engine)
    finally:
        engine.dispose()


def main() -> None:
    """Start the application and explain startup errors."""
    options = read_arguments()

    try:
        run_application(options)
    except (OSError, UnicodeError) as error:
        print(f"Unable to access an application file: {error}")
    except LarkError as error:
        print(f"Invalid grammar: {error}")
    except SQLAlchemyError:
        print("Unable to access the database. Please try again.")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    except Exception:
        print("The application stopped because of an unexpected error.")


if __name__ == "__main__":
    main()
