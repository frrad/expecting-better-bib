#!/usr/bin/python3

import toml
import crossref_commons.retrieval
from pytablewriter import MarkdownTableWriter

filename = "data.toml"
filename_md = "README.md"

with open(filename, "r") as f:
    data_bytes = f.read()


data = toml.loads(data_bytes)

NAME = "name"
DOI = "doi"
# curl --silent http://api.crossref.org/styles | jq .message.items | sort | tail -n +3 | less
STYLE = {
    "AMA": "american-medical-association",
    "APA": "apa-no-doi-no-issue",
    "IEEE": "ieee",
    "MLA": "modern-language-association",
}
NUM = "number"


def linkify(doi):
    SITE = "https://doi.org/%s"
    LINK = SITE % doi
    return "[%s](%s)" % (doi, LINK)


for chap in data:
    for cite in data[chap]:
        if cite[DOI] != "" and (NAME not in cite or cite[NAME] == ""):
            metadata = crossref_commons.retrieval.get_publication_as_refstring(
                cite[DOI], STYLE["APA"]
            )

            metadata = metadata.strip()
            cite[NAME] = metadata

with open(filename, "w") as f:
    f.write(toml.dumps(data))


chap_str = ""

for chap in data:
    rows = []
    for cite in data[chap]:
        rows.append([cite[NUM], cite[NAME], linkify(cite[DOI])])

    writer = MarkdownTableWriter(
        table_name=chap, headers=["#", "Citation", "DOI"], value_matrix=rows
    )

    chap_str += writer.dumps()
    chap_str += "\n"

with open(filename_md, "w") as f:
    f.write(chap_str)
