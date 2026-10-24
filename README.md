# Talk Shop

Mini projekt 1 — chatbot sklepu w Pythonie z biblioteką Lark.

## Funkcje

- Wielokrotne zadawanie pytań.
- Zakończenie rozmowy przez wpisanie END.
- Czytelne komunikaty o błędach.
- Wczytywanie gramatyki z pliku przez parametr -g lub --grammar.
- Pytania o cenę, dostępność i liczbę produktów.

## Uruchomienie

Wymagane: Python 3.13 lub nowszy oraz uv.

W terminalu, w katalogu projektu:

```sh
uv sync --all-groups
uv run talk-shop -g grammar.txt
```

Alternatywnie:

```sh
uv run talk-shop --grammar grammar.txt
```

## Przykładowe pytania

```text
how much is monorail
is compaq in stock
do you have any compaq
how many compaq do you have
how many monorail are in stock
how much is the hewlett_packard
END
```

Dostępne produkty: monorail, compaq, hewlett_packard.
Pytania zadajemy po angielsku.
Nieznany produkt lub nierozpoznane pytanie nie przerywają rozmowy.

