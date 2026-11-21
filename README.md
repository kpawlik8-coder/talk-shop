# Talk Shop

Chatbot sklepu napisany w Pythonie z wykorzystaniem Lark,
SQLAlchemy i bazy SQLite.

## Funkcje

- Pytania o cenę, dostępność i liczbę produktów.
- Pobieranie danych z bazy.
- Wielokrotne zadawanie pytań; END kończy rozmowę.
- Komunikaty wyjaśniające błędne pytania.
- Wczytywanie gramatyki przez -g lub --grammar.
- Tryb administratora do zarządzania produktami.

## Przygotowanie

Wymagane: Python 3.13 lub nowszy oraz uv.

W katalogu projektu wykonaj:

```sh
uv sync --all-groups
```

Baza SQLite jest tworzona automatycznie w local/shop.db.
Dane pozostają zapisane po zamknięciu programu.
Folder local jest pomijany przez Git.

Przy pierwszym uruchomieniu baza jest pusta.
Dodaj produkty w trybie administratora przed użyciem chatbota.

## Tryb administratora

```sh
uv run talk-shop --admin
```

Menu:

1. Dodaj produkt.
2. Znajdź produkt.
3. Zmień produkt.
4. Usuń produkt.
5. Lista produktów.
6. Wyczyść bazę danych.
0. Zakończ.

Zmiana produktu wymaga podania wszystkich nowych danych:
nazwy, ceny i stanu.

Usunięcie produktu wymaga potwierdzenia YES.
Wyczyszczenie bazy wymaga potwierdzenia CLEAR.

Nazwa produktu powinna zawierać angielskie litery i spacje.
Można również używać podkreśleń, które są zamieniane na spacje.
Nazwy produktów nie mogą się powtarzać niezależnie od wielkości liter.

Cena musi być skończoną liczbą nieujemną.
Stan musi być nieujemną liczbą całkowitą.

## Tryb użytkownika

```sh
uv run talk-shop -g src/talk_shop/static/grammar.txt
```

Alternatywnie:

```sh
uv run talk-shop --grammar src/talk_shop/static/grammar.txt
```

Po dodaniu produktu COMPAQ można zapytać:

```text
how much is compaq
is compaq in stock
how many compaq do you have
END
```

W pytaniach nazwy wielowyrazowe zapisujemy z podkreśleniami,
np. test_laptop dla produktu Test Laptop.

Interakcja z programem odbywa się po angielsku.

## Testy

```sh
uv run python -m unittest discover -s tests -v
```

Testy korzystają z osobnej bazy w pamięci.
Nie modyfikują danych w local/shop.db.

## Autorzy

- Kacper Pawlik — rozwinięcie projektu.
- Kod wyjściowy i przykłady dydaktyczne: Piotr Gnyś.