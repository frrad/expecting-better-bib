#!/usr/bin/python3

from pytablewriter import MarkdownTableWriter
import crossref_commons.retrieval
import requests
import toml

filename = "data.toml"
filename_md = "BIBLIOGRAPHY.md"

NAME = "name"
DOI = "doi"
ISBN = "isbn"

ISBN_FORMAT_STRING = "https://www.google.com/search?tbm=bks&q=isbn:%s"
DOI_FORMAT_STRING = "https://doi.org/%s"


# curl --silent http://api.crossref.org/styles | jq .message.items | sort | tail -n +3 | less
STYLE = {
    "AMA": "american-medical-association",
    "APA": "apa-no-doi-no-issue",
    "IEEE": "ieee",
    "MLA": "modern-language-association",
}
NUM = "number"


def linkify(doi):
    link = DOI_FORMAT_STRING % doi
    return "[%s](%s)" % (doi, link)


def linkify_isbn(isbn):
    link = ISBN_FORMAT_STRING % isbn
    return "[%s](%s)" % (isbn, link)


def author_string_from_list(authors):
    string = authors[0]

    for i, a in enumerate(authors[1:]):
        if i == len(authors) - 2:
            string += ", and " + a
        else:
            string += ", " + a

    return string


def book_from_isbn(isbn):
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}".format(isbn)
    r = requests.get(url)
    info = r.json()["items"][0]["volumeInfo"]

    info["authorString"] = author_string_from_list(info["authors"])

    # change if no subtitle
    info["titleAndSubtitle"] = "{title}: {subtitle}".format(**info)

    return "{authorString}, _{titleAndSubtitle}_ ({publisher}, {publishedDate})".format(
        **info
    )


def main():
    with open(filename, "r") as f:
        data_bytes = f.read()

    data = toml.loads(data_bytes)

    for chap in data:
        for cite in data[chap]:
            if (
                DOI in cite
                and cite[DOI] != ""
                and (NAME not in cite or cite[NAME] == "")
            ):
                metadata = crossref_commons.retrieval.get_publication_as_refstring(
                    cite[DOI], STYLE["APA"]
                )

                metadata = metadata.strip()
                cite[NAME] = metadata

            if (
                ISBN in cite
                and cite[ISBN] != ""
                and (NAME not in cite or cite[NAME] == "")
            ):
                cite[NAME] = book_from_isbn(cite[ISBN])

    with open(filename, "w") as f:
        f.write(toml.dumps(data))

    chap_str = ""

    for chap in data:
        rows = []
        for cite in data[chap]:
            if DOI in cite:
                rows.append([cite[NUM], cite[NAME], linkify(cite[DOI])])
            elif ISBN in cite:
                rows.append([cite[NUM], cite[NAME], linkify_isbn(cite[ISBN])])
            else:
                rows.append([cite[NUM], cite[NAME], ""])

        writer = MarkdownTableWriter(
            table_name=chap, headers=["#", "Citation", "DOI / ISBN"], value_matrix=rows
        )

        chap_str += writer.dumps()
        chap_str += "\n"

    with open(filename_md, "w") as f:
        f.write(chap_str)


if __name__ == "__main__":
    main()
