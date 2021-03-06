#!/usr/bin/python3

import toml
import crossref_commons.retrieval
from pytablewriter import MarkdownTableWriter

filename = "data.toml"
filename_md = "output.md"

with open(filename, "r") as f:
    data_bytes = f.read()


data = toml.loads(data_bytes)

NAME = "name"
DOI = "doi"
STYLE = "american-medical-association"  # http://api.crossref.org/styles


def linkify(doi):
    return "[%s](https://doi.org/%s)" % (doi, doi)


for chap in data:
    for citation in data[chap]:
        cite = data[chap][citation]
        print(cite[DOI])

        if cite[DOI] != "" and (NAME not in cite or cite[NAME] == ""):
            metadata = crossref_commons.retrieval.get_publication_as_refstring(
                cite[DOI], STYLE
            )

            metadata = metadata.strip()
            cite[NAME] = metadata


with open(filename, "w") as f:
    f.write(toml.dumps(data))


chap_str = ""

for chap in data:
    rows = []
    for citation in data[chap]:
        cite = data[chap][citation]
        rows.append([citation, cite[NAME], linkify(cite[DOI])])

    writer = MarkdownTableWriter(
        table_name=chap, headers=["#", "Citation", "DOI"], value_matrix=rows
    )

    chap_str += writer.dumps()
    chap_str += "\n"

with open(filename_md, "w") as f:
    f.write(chap_str)
