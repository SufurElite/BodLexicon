#!/bin/python3
import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection_obj = sqlite3.connect("variants.db")
connection_obj.execute("PRAGMA foreign_keys = ON;")


def create_tables():
    cursor_obj = connection_obj.cursor()
    all_tables_creation = """
        CREATE TABLE manuscripts (
            title TEXT PRIMARY KEY NOT NULL,
            text TEXT NOT NULL
        );
        CREATE TABLE variants (
            word TEXT PRIMARY KEY NOT NULL,
            count INTEGER NOT NULL
        );
        CREATE TABLE variant_occurrences (
            word TEXT NOT NULL,
            manuscript_title TEXT NOT NULL,
            PRIMARY KEY (word, manuscript_title),
            FOREIGN KEY (word) REFERENCES variants(word),
            FOREIGN KEY (manuscript_title) REFERENCES manuscripts(title)
        );
        CREATE TABLE word_pairs (
            word_a TEXT NOT NULL,
            word_b TEXT NOT NULL,
            PRIMARY KEY (word_a, word_b)
        );
    """
    # Execute the table creation query
    cursor_obj.executescript(all_tables_creation)
    connection_obj.commit()


def populate_manuscript(manuscript_data: list):
    manuscript_formatted = []
    for idx in range(len(manuscript_data)):
        text = manuscript_data[idx]["text"]
        title = manuscript_data[idx]["title"]
        manuscript_formatted.append((title, text))
    connection_obj.executemany(
        "insert into manuscripts(title, text) values (?,?)", manuscript_formatted
    )
    connection_obj.commit()


def populate_variants(variant_data: dict):
    variants = []
    for variant in variant_data:
        count = variant_data[variant]["count"]
        variants.append((variant, count))
    connection_obj.executemany(
        "insert into variants(word, count) values (?,?)", variants
    )
    connection_obj.commit()


def populate_variant_occurrences(variant_data: dict):
    variant_occurences = []
    for variant in variant_data:
        seen = set()
        for title in variant_data[variant]["texts"]:
            if title not in seen:
                variant_occurences.append((variant, title))
                seen.add(title)
    connection_obj.executemany(
        "insert into variant_occurrences(word, manuscript_title) values (?,?)",
        variant_occurences,
    )
    connection_obj.commit()


def populate_word_pairs(word_pairs: set):
    word_pairs_list = list(word_pairs)
    connection_obj.executemany(
        "insert into word_pairs(word_a, word_b) values (?,?)", word_pairs_list
    )
    connection_obj.commit()


if __name__ == "__main__":
    create_tables()
