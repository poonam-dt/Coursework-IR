import os
import ast
from searchEnginePublications_copy.searchEnginePublications.spiders.publications_abstract import update, begin, \
    PublicationSpider_1
import json

global inverted_index


def implement_inverted_index(document_list_index):
    # dictonary for an inverted index
    inverted_n = {}
    for i, doc in enumerate(document_list_index):
        for term in doc:
            if term in inverted_n:
                inverted_n[term].add(i)
            else:
                inverted_n[term] = {i}

    # writing index to putput.txt
    with open('output.txt', 'w', encoding="utf-8") as output:
        output.write(f"{inverted_n}")


def update_implemented_inverted_index(document_updated_list):
    for i, doc in enumerate(document_updated_list):
        for term in doc:
            if term in inverted_index:
                inverted_index[term].add(i)
            else:
                inverted_index[term] = {i}

    # Add the updated index with the existing index
    try:
        with open('output.txt', 'r', encoding="utf-8") as f:
            existing_index = ast.literal_eval(f.read())
    except FileNotFoundError:
        existing_index = {}

    for term, postings in inverted_index.items():
        if term in existing_index:
            existing_index[term].update(postings)
        else:
            existing_index[term] = postings

    # Save the merged index to the output file
    with open('output.txt', 'w', encoding="utf-8") as f:
        f.write(f"{existing_index}")


try:
    with open('output.txt', encoding="utf-8") as file:
        content = file.read()

except FileNotFoundError:
    begin.crawl(PublicationSpider_1)
    begin.start()
    documents_pub = document_preprocessor("documents.json")
    list_of_documents = documents_pub['words'].to_list()
    implement_inverted_index(list_of_documents)

else:
    inverted_index = ast.literal_eval(content)
    update.crawl(PublicationSpider_1)
    update.start()
    updated_document = document_preprocessor("update.json")
    updated_document_list = updated_document['words'].to_list()
    update_implemented_inverted_index(updated_document_list)
    # check data from update.json
    with open('update.json', 'r') as f:
        data = json.load(f)

    # write data into documents_pub.json
    if os.path.exists('documents.json') and os.path.isfile('documents.json'):
        os.remove('documents.json')

    with open('documents.json', 'w') as f:
        json.dump(data, f)

    if os.path.exists('update.json') and os.path.isfile('update.json'):
        os.remove('update.json')