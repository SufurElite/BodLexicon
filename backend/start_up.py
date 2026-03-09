import sqlite3


def init_map():
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
    return variant_map
