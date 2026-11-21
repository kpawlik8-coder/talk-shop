"""Test database operations and chatbot responses using a temporary database."""

import unittest
from pathlib import Path

from sqlalchemy import create_engine

from talk_shop.core.products import (
    add_product,
    clear_db,
    delete_product,
    find_product,
    list_products,
    update_product,
)
from talk_shop.models.product import DatabaseModel, Product
from talk_shop.talk_shop import load_parser, process_query


PROJECT_DIR = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = PROJECT_DIR / "src" / "talk_shop" / "static" / "grammar.txt"


class ShopTests(unittest.TestCase):
    """Check database operations and the chatbot using isolated data."""

    def setUp(self):
        """Create a fresh database in memory for each test."""
        self.engine = create_engine("sqlite:///:memory:")
        self.addCleanup(self.engine.dispose)
        DatabaseModel.metadata.create_all(self.engine)
        self.parser = load_parser(str(GRAMMAR_PATH))
        add_product(Product("COMPAQ", 2399.99, 8), self.engine)

    def test_find_product(self):
        """Find a saved product regardless of letter case."""
        product = find_product("compaq", self.engine)

        self.assertIsNotNone(product)
        self.assertEqual(product, Product("COMPAQ", 2399.99, 8))

    def test_list_products(self):
        """Return all saved products."""
        add_product(Product("Monorail", 1449.99, 30), self.engine)

        names = [product.name for product in list_products(self.engine)]

        self.assertCountEqual(names, ["COMPAQ", "Monorail"])

    def test_update_product(self):
        """Save changed details and make them available to the chatbot."""
        updated = update_product(
            "compaq",
            Product("COMPAQ", 125.0, 0),
            self.engine,
        )

        self.assertTrue(updated)
        self.assertEqual(
            find_product("compaq", self.engine),
            Product("COMPAQ", 125.0, 0),
        )
        self.assertIn(
            "125.00$",
            process_query("how much is compaq", self.parser, self.engine),
        )
        self.assertIn(
            "out of stock",
            process_query("is compaq in stock", self.parser, self.engine),
        )

    def test_delete_product(self):
        """Remove a product and report when it no longer exists."""
        self.assertTrue(delete_product("compaq", self.engine))
        self.assertIsNone(find_product("compaq", self.engine))
        self.assertFalse(delete_product("compaq", self.engine))

    def test_clear_database(self):
        """Remove all products and keep the table usable."""
        add_product(Product("Monorail", 1449.99, 30), self.engine)

        clear_db(self.engine)

        self.assertEqual(list_products(self.engine), [])

        add_product(Product("Laptop", 100.0, 2), self.engine)
        self.assertEqual(len(list_products(self.engine)), 1)

    def test_duplicate_name(self):
        """Reject a duplicate name without changing the original product."""
        with self.assertRaises(ValueError):
            add_product(Product("compaq", 100.0, 1), self.engine)

        self.assertEqual(
            find_product("compaq", self.engine),
            Product("COMPAQ", 2399.99, 8),
        )

    def test_invalid_product_data(self):
        """Reject empty names, invalid prices and invalid stock."""
        invalid_products = [
            Product("", 10.0, 1),
            Product("Laptop", -1.0, 1),
            Product("Laptop", float("nan"), 1),
            Product("Laptop", float("inf"), 1),
            Product("Laptop", 10.0, -1),
            Product("Laptop", 10.0, 1.5),
        ]

        for product in invalid_products:
            with self.subTest(product=product):
                with self.assertRaises(ValueError):
                    add_product(product, self.engine)

        self.assertEqual(len(list_products(self.engine)), 1)

    def test_questions(self):
        """Answer supported questions and explain invalid input."""
        cases = {
            "How much is compaq?": "2399.99$",
            "is compaq in stock": "Yes, COMPAQ",
            "how many compaq do you have": "8 units",
            "how much is jacket": "could not find that product",
            "hello": "could not understand",
            "": "could not understand",
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                response = process_query(query, self.parser, self.engine)
                self.assertIn(expected, response)

    def test_name_with_spaces(self):
        """Find a multiword product using underscores in the question."""
        add_product(Product("Test Laptop", 125.0, 3), self.engine)

        response = process_query(
            "how much is test_laptop",
            self.parser,
            self.engine,
        )

        self.assertIn("125.00$", response)


if __name__ == "__main__":
    unittest.main()
