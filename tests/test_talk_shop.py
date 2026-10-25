import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from talk_shop.talk_shop import load_parser, main, process_query, products


PROJECT_DIR = Path(__file__).resolve().parents[1]
GRAMMAR_PATH = PROJECT_DIR / "src" / "talk_shop" / "static" / "grammar.txt"

class ShopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = load_parser(str(GRAMMAR_PATH))

    def test_questions(self):
        cases = {
            "How much is the monorail?": "1449.99$",
            "how much is hewlett_packard": "1849.99$",
            "is the compaq in stock": "Yes, COMPAQ",
            "do you have any compaq": "Yes, COMPAQ",
            "how many compaq are in stock": "8 units",
            "how many hewlett_packard do you have": "23 units",
            "how much is jacket": "I could not find that product in our shop.",
            "hello": "could not understand",
            "": "could not understand",
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                response = process_query(query, self.parser)
                self.assertIn(expected, response)

    def test_out_of_stock(self):
        with patch.object(products["compaq"], "stock", 0):
            availability = process_query(
                "is compaq in stock", self.parser
            )
            quantity = process_query(
                "how many compaq do you have", self.parser
            )

        self.assertIn("out of stock", availability)
        self.assertIn("0 units", quantity)

    def run_dialog(self, grammar_path, inputs):
        output = io.StringIO()
        arguments = ["talk-shop", "-g", str(grammar_path)]

        with patch("sys.argv", arguments):
            with patch("builtins.input", side_effect=inputs):
                with contextlib.redirect_stdout(output):
                    main()

        return output.getvalue()

    def test_dialog_continues_after_error(self):
        output = self.run_dialog(
            GRAMMAR_PATH,
            ["hello", "how much is compaq", " END "],
        )

        self.assertIn("could not understand", output)
        self.assertIn("2399.99$", output)
        self.assertIn("Goodbye!", output)

    def test_input_termination(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error):
                output = self.run_dialog(GRAMMAR_PATH, [error])
                self.assertIn("Goodbye!", output)

    def test_missing_grammar(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_file = Path(directory) / "missing.txt"
            output = self.run_dialog(missing_file, [])

        self.assertIn("Unable to read the grammar file", output)

    def test_invalid_grammar(self):
        with tempfile.TemporaryDirectory() as directory:
            grammar_file = Path(directory) / "grammar.txt"
            grammar_file.write_text("start: [", encoding="utf-8")
            output = self.run_dialog(grammar_file, [])

        self.assertIn("Invalid grammar", output)


if __name__ == "__main__":
    unittest.main()