import sqlite3
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from nltk.tokenize.punkt import PunktLanguageVars

app = Flask(__name__)
CORS(app)
p = PunktLanguageVars()


variant_map = {}

manuscripts = {}


def load_values():
    con = sqlite3.connect("variants.db")
    cur = con.cursor()
    res = cur.execute("SELECT word_a, word_b FROM word_pairs")
    word_pairs = res.fetchall()

    res = cur.execute("SELECT word, count FROM variants")
    variants = res.fetchall()
    variant_count = {}
    for pair in variants:
        variant_count[pair[0]] = pair[1]

    res = cur.execute("SELECT word, manuscript_title FROM variant_occurrences")
    variant_occurences = res.fetchall()
    variant_to_works = {}
    for pair in variant_occurences:
        if pair[0] not in variant_to_works:
            variant_to_works[pair[0]] = []
        variant_to_works[pair[0]].append(pair[1])

    global variant_map
    variant_map = {}
    reverse_tuple = set()
    for pair in word_pairs:
        if pair in reverse_tuple:
            continue
        reverse_tuple.add((pair[1], pair[0]))
        if pair[0] not in variant_map:
            variant_map[pair[0]] = {
                "id": pair[0],
                "forms": [pair[0]],
                "works": variant_to_works[pair[0]],
                "spellings": [{"form": pair[0], "count": variant_count[pair[0]]}],
            }
        if pair[1] not in variant_map:
            variant_map[pair[1]] = {
                "id": pair[1],
                "forms": [pair[1]],
                "works": variant_to_works[pair[1]],
                "spellings": [{"form": pair[1], "count": variant_count[pair[1]]}],
            }

        variant_map[pair[0]]["forms"].append(pair[1])
        variant_map[pair[1]]["forms"].append(pair[0])

        variant_map[pair[0]]["spellings"].append(
            {"form": pair[1], "count": variant_count[pair[1]]}
        )
        variant_map[pair[1]]["spellings"].append(
            {"form": pair[0], "count": variant_count[pair[0]]}
        )
    con.close()


def split_into_paragraphs(tokens, max_tokens_per_paragraph=50):
    """
    Split a flat list of tokens into multiple paragraphs.
    Each paragraph is a list of tokens.
    """
    paragraphs = []
    current_para = []
    count = 0

    for tok in tokens:
        current_para.append(tok)
        count += 1

        # If we reach max tokens, end paragraph
        if count >= max_tokens_per_paragraph:
            paragraphs.append(current_para)
            current_para = []
            count = 0

    # Add leftover tokens as last paragraph
    if current_para:
        paragraphs.append(current_para)

    return paragraphs


@app.route("/init", methods=["GET"])
def start_up():
    con = sqlite3.connect("variants.db")
    cur = con.cursor()
    variants = []
    # let's get all word variations and their counts

    res = cur.execute("SELECT title, text FROM manuscripts")
    manuscripts = res.fetchall()
    pages = []
    for manuscript in manuscripts:
        text = manuscript[1].replace("\n", " ").replace("¶", " ").replace("//", " ")
        tokens = p.word_tokenize(text.lower())
        sentences = []
        current_sent = []
        for token in tokens:
            if token in variant_map:
                variants.append(variant_map[token])
                sentences.append(" ".join(current_sent) + " ")
                sentences.append({"type": "variant", "id": token, "form": token})
                current_sent = [" "]
            else:
                current_sent.append(token)
        if current_sent != []:
            sentences.append(" ".join(current_sent))
        paragraphs = split_into_paragraphs(sentences, max_tokens_per_paragraph=60)
        pages.append({"label": manuscript[0], "paragraphs": paragraphs})
    con.close()

    #

    # select all the pages (maybe later I'll just do a subsection)

    result = {
        "manuscript": {"title": "Vernon Manuscript", "repository": "Bodleian Library"},
        "variants": variants,
        "pages": pages,
    }

    return jsonify(result)


if __name__ == "__main__":
    load_values()
    app.run(host="0.0.0.0", port=8080, debug=True)
