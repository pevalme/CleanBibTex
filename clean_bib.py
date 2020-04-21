#!/usr/bin/env python3

import sys

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

import requests

import progressbar

if __name__ == "__main__":
    if len(sys.argv) is not 3:
        print("Usage: ./clean_bib.py file.bib clean.bib")
        sys.exit(0)

    urlBase = "https://dblp.org/search/publ/api?"

    db = BibDatabase()
    errors = []

    print("Cleaning .bibtex bibliography with dblp")
    print("\033[1;34mThis tool leaves unchanged books, thesis and all items that cannot be found on https://dblp.org\033[0m")
    
    with open(sys.argv[1]) as bibFile:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bibData = parser.parse_file(bibFile)

    bar = progressbar.ProgressBar(len(bibData.entries)).start()
    n = 0

    for b in bibData.entries:
        if b["ENTRYTYPE"] == "book" or "thesis" in b["ENTRYTYPE"].lower():
            db.entries.append(b)
            n = n + 1
            continue

        while b["title"][0] == '{' and b["title"][2] != '}':
            b["title"] = b["title"][1:-1]

        url = urlBase + "q=" + b["title"].replace(" ","+") + "&format=bib"
        dblp = requests.get(url)

        result = bibtexparser.loads(dblp.content)
        if len(result.entries) == 0:
            errors.append("\033[1;31m" + b["ID"] + "\033[0m" + ": " + b["title"])
            db.entries.append(b)
        else:
            result.entries[0]["ID"] = b["ID"]
            db.entries.append(result.entries[0])

        n = n + 1
        bar.update(n)

    print()

    if len(errors):
        print("Encountered " + str(len(errors)) + " errors")
        for e in errors:
            print(e)
    else:
        print("\034[1;31mAll entries found in dblp\033[0m")
    
    print("\nDumping data into <" + sys.argv[2] + ">")

    with open(sys.argv[2], 'w') as bibtex_file:
        bibtexparser.dump(db, bibtex_file)