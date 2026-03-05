#!/bin/python3

"""
This file ties together the different preprocessing components that need
to occur to run the program.
"""

from download import download_iiif
from download import get_text_pages
from preprocess import (
    Language,
    preprocess_middle_english,
    COLUMN_RE,
    find_variants,
    get_stop_words,
)
from database_creation import (
    create_tables,
    populate_manuscript,
    populate_variants,
    populate_variant_occurrences,
    populate_word_pairs,
)
# TODO add command line argumentation to enable ease of customisation


def main():
    total_json = download_iiif()
    # form of {"title":"fol title", "text": "text joined together with \n"}
    text_pages = get_text_pages(total_json)
    # this is the count of variants of a particular spelling for a word
    running_count = {}
    # words of similar spelling
    word_pairs = set()

    MIDDLE_ENGLISH_STOP_WORDS = set(get_stop_words(Language.MiddleEnglish))

    for idx in range(len(text_pages)):
        value = text_pages[idx]
        assert isinstance(value, dict)
        value["text"] = COLUMN_RE.sub(" ", value["text"])
        text = value["text"].replace("\n", " ")
        title = value["title"]
        value["text_for_analysis"] = preprocess_middle_english(text=text)
        running_count, word_pairs = find_variants(
            text=value["text_for_analysis"],
            running_count=running_count,
            word_pairs=word_pairs,
            title=title,
            stop_words=MIDDLE_ENGLISH_STOP_WORDS,
        )
    # Having derived the above stats and variants,
    # we proceed with creating the database necessary
    create_tables()
    populate_manuscript(text_pages)
    populate_variants(running_count)
    populate_variant_occurrences(running_count)
    populate_word_pairs(word_pairs)


if __name__ == "__main__":
    main()
