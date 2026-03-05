#!/bin/python3
import requests
import urllib.request
import json
import sys
from bs4 import BeautifulSoup
from typing import List, Callable

# the default URL is for Oxford's Vernon Manuscript
DEFAULT_URL = "https://iiif.bodleian.ox.ac.uk/iiif/manifest/52f0a31a-1478-40e4-b05b-fddb1ad076ff.json"

DEFAULT_HEADERS = {
    "Accept": "application/ld+json;profile=http://iiif.io/api/presentation/3/context.json",
    "Content-Type": "application/json",
}

SUBSET_FILTERS = [{"type": "Range", "label": {"en": ["Piers Plowman"]}}]

"""
TODO 
experiment with just using 
{
                  "label": {
                    "en": [
                      "Language"
                    ]
                  },
                  "value": {
                    "en": [
                      "English, Middle (1100-1500)"
                    ]
                  }
                }

as a filter? 
"""


def vernon_filter(total_json: dict, filters: List):
    """
    params:
        total_json (dict) - the IIIF json with the manuscript
        filters (List[dict]) - the subfilter we want to supplant to filter out particular sections
    Returns:
        A list of html links to grab text from for subsequent preprocessing

    This is the default filter, but since we're passing in a function to be used, it's easily supplantable
    with a different function following a similar format.
    """
    pages_to_identify = []

    values = total_json["structures"][0]  # a jsonl/list of dictionaries
    search_values = values["items"]
    while len(search_values) != 0:
        current_value = search_values.pop()
        for tmp_filter in filters:
            if tmp_filter.items() <= current_value.items():
                pages_to_identify += current_value["items"]

        if "items" in current_value:
            search_values += current_value["items"]
    html_files = []
    for val in pages_to_identify:
        id = val["id"]
        end_idx = id.rfind("/") + 1
        json_idx = id.find(".json")
        uuid = id[end_idx:json_idx]
        html_files.append(
            f"https://iiif.bodleian.ox.ac.uk/text/52f0a31a-1478-40e4-b05b-fddb1ad076ff/vernon-transcription/html/{uuid}.html"
        )
    return html_files


def get_all_html():
    return []


def download_iiif(url: str = DEFAULT_URL, headers: dict = DEFAULT_HEADERS) -> dict:
    """
    params:
        url (str) - the iiif url that we want to download from

    Runs the GET request to retrieve the totality of the manuscript in JSON format
    """

    # We need to make the relevant GET request to download the json
    response = requests.get(url=DEFAULT_URL, headers=headers)
    if response.status_code != 200:
        sys.stderr.write(
            f"Error reaching out to {url}; encountered response status of {response.status_code}\n"
        )
        sys.exit(1)
    return response.json()


def html_link_to_text(url: str):
    """
    params:
        url (str) - the url that we're going to parse the text from
    returns:
        the a json of title and text (lines joined by newline)
    """
    fp = urllib.request.urlopen(url)
    url_bytes = fp.read()

    html_content = url_bytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(html_content, "html.parser")
    # the title can be used as metadata to record the title of the given page
    title = soup.find("title").text
    divs = soup.find_all("div")
    texts = "\n".join([div.text for div in divs])

    return {"title": title, "text": texts}


def get_text_pages(
    total_json: dict, filters: List = SUBSET_FILTERS, filter: Callable = vernon_filter
):
    """
    Params:
        total_json (dict) - given the JSON of the manuscript, we look for
        SUBSET_FILTERS (List) - a List of possible filters we want to apply to the JSON to
        retrieve a subset of the totality of the IIIF manuscript in question
    # TODO update the way the subset filter works so it's easily adjustable with some command line arguments
    as of right now it is very much dependent on the format presetned for the Vernon Manuscripts
    namely,
        * if nothing is in the SUBSET_FILTERS we grab all the available text by going to through the items section
    and finding the parts that have a "rendering" with an html to go to
        * with the subset provided (in the default case we look at Piers Plowman) and retrieve the relevant range
        sections that follow
    """
    assert (
        "items" in total_json
    ), "Expected to find 'items' in the downloaded iiif json for the manuscript, but it wasn't found"

    ## TODO add logging

    # current approach, if a filter isn't provided we go through items and look at the renderings
    # otherwise we look at structures and try to find the filter
    html_pages = filter(total_json, filters) if filters != [] else get_all_html()

    # and now we convert these pages to their html counterparts given their id
    return [html_link_to_text(html_page) for html_page in html_pages]


def test():
    # total_json = download_iiif()
    with open("tmp_download.json", "r") as f:
        total_json = json.load(f)
    get_text_pages(total_json)


if __name__ == "__main__":
    test()
