#!/bin/python3

import re
from enum import Enum
from cltk.stop.middle_english.stops import STOPS_LIST
from nltk.tokenize.punkt import PunktLanguageVars

p = PunktLanguageVars()


class Language(Enum):
    MiddleEnglish = 1


def get_stop_words(language: Language):
    """ """
    if language == Language.MiddleEnglish:
        return STOPS_LIST


COLUMN_RE = re.compile(r"\[Column\s+[^\]]+\]", re.IGNORECASE)

# Roman numerals excluding single I
ROMAN_RE = re.compile(
    r"\b(?!I\b)(?:M{0,4}(CM|CD|D?C{0,3})" r"(XC|XL|L?X{0,3})" r"(IX|IV|V?I{2,3}|V))\b",
    re.IGNORECASE,
)

VOWELS = "aeiouyæœ"


def consonant_skeleton(word):
    return "".join(c for c in word if c not in VOWELS)


def plausible_variant(a, b):
    return consonant_skeleton(a) == consonant_skeleton(b)


def preprocess_middle_english(text: str, abbr_marker="ː") -> str:
    """
    Both preprocess the text so that it's ready for analysis, but also so it corresponds
    to the page
    """
    # 1. Remove ¶ and //
    text = text.replace("¶", " ")
    text = text.replace("//", " ")

    # 2. Merge tilde word breaks
    text = re.sub(r"(\w+)~\s*(\w+)", r"\1\2", text)

    # 3. Mark internal abbreviations like wy[m]an -> wyːan
    text = re.sub(
        r"(\w*)\[([^\]]+)\](\w*)",
        lambda m: f"{m.group(1)}{abbr_marker}{m.group(3)}"
        if m.group(1) or m.group(3)
        else f"{abbr_marker}{m.group(2)}{abbr_marker}",
        text,
    )

    # 4. Mark whole bracketed words like [and]
    text = re.sub(r"\[([A-Za-zȜȝÞþé]+)\]", rf"{abbr_marker}\1{abbr_marker}", text)

    # 5. Remove Roman numerals except I
    text = ROMAN_RE.sub(" ", text)

    # 6. Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def levenshtein(a: str, b: str, max_dist: int | None = None) -> int:
    """
    Compute the Levenshtein distance between strings a and b.

    If max_dist is provided, computation stops early if the distance
    must exceed max_dist. In that case, returns max_dist + 1.
    """

    la, lb = len(a), len(b)

    # Quick length-based cutoff
    if max_dist is not None and abs(la - lb) > max_dist:
        return max_dist + 1

    # Ensure a is the shorter string (reduces memory slightly)
    if la > lb:
        a, b = b, a
        la, lb = lb, la

    prev = list(range(la + 1))

    for j in range(1, lb + 1):
        cur = [j] + [0] * la
        bj = b[j - 1]

        row_min = cur[0]

        for i in range(1, la + 1):
            cost = 0 if a[i - 1] == bj else 1

            cur[i] = min(
                prev[i] + 1,  # deletion
                cur[i - 1] + 1,  # insertion
                prev[i - 1] + cost,  # substitution
            )

            row_min = min(row_min, cur[i])

        # Early stopping
        if max_dist is not None and row_min > max_dist:
            return max_dist + 1

        prev = cur

    return prev[la]


def find_variants(
    text: str, running_count: dict, word_pairs: set, stop_words: set, title: str
):
    """
    params:
        text (str) - the text that we're parsing
        running_count (dict) - a dictionary of the running count of spellings for variants
        word_pairs (dict) - the word to word correspondence to
        stop_words (set) - the set of words that we are common to ME (articles, conjunctions, etc.)
        max_threshold_parameter (int) - custom threshold to determine the maximum amount of similarity edits allowed for the distance
        to be calculated. We only want to find variants of spelling of words. By default the value is 2.
    """
    tokens = p.word_tokenize(text.lower())
    # ignore tokens of one length and common Middle English tokens
    unique_toks = [w for w in tokens if w not in stop_words and len(w) != 1]
    for tok in unique_toks:
        if tok not in running_count:
            running_count[tok] = {"count": 0, "texts": [title]}
        running_count[tok]["count"] += 1
        running_count[tok]["texts"].append(title)

    for tok in unique_toks:
        for word in running_count:
            if (
                word == tok
                or (tok, word) in word_pairs
                or abs(len(word) - len(tok)) > 2
            ):
                continue

            if consonant_skeleton(tok) != consonant_skeleton(word):
                continue

            max_dist = 1
            if len(tok) <= 4:
                max_dist = 1
            elif len(tok) < 9:
                max_dist = 2
            else:
                max_dist = 3
            dist = levenshtein(tok, word, max_dist=max_dist)
            ratio = dist / max(len(word), len(tok))
            # look at a normalized distance
            if ratio <= 0.3:
                # for now we'll make it symmetric as it'll make things easier later
                word_pairs.add((word, tok))
                word_pairs.add((tok, word))

    return running_count, word_pairs


if __name__ == "__main__":
    print(levenshtein("kitten", "sitting"))
    # 3

    print(levenshtein("kitten", "sitting", max_dist=2))
