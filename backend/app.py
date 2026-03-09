import sqlite3
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from nltk.tokenize.punkt import PunktLanguageVars
from start_up import init_map

manuscripts = {}
variant_map = init_map()

app = Flask(__name__)
CORS(app)
p = PunktLanguageVars()


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

    # select all the pages (maybe later I'll just do a subsection)

    result = {
        "manuscript": {"title": "Vernon Manuscript", "repository": "Bodleian Library"},
        "variants": variants,
        "pages": pages,
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
