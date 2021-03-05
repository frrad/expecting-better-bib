import toml
import crossref_commons.retrieval

filename = "data.toml"

with open(filename, "r") as f:
    data_bytes = f.read()


data = toml.loads(data_bytes)

NAME = "name"
DOI = "doi"
STYLE = "apa"  # http://api.crossref.org/styles

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
