
import ast
import math
from itertools import count
import numpy as np
from preprocessing_publications import *
import PySimpleGUI as sg
import webbrowser
display_result = {}
results_list = []
num = 2
start = 0
limit = 1000000
label_list = []
separator_list = []
button_back = ""
button_forward = ""
status = ""
documents = document_preprocessor("documents.json")


def normalize_document(document, query, idf):

    document_normalized = {}

    # calculating document tf-idf
    for doc in document:
        tf_idf_list_doc = []
        page = documents['words'].iloc[doc]

        for word in query:
            index = query.index(word)
            frequency = page.count(word)
            weighted_frequency = math.log(frequency + 1)
            tf_idf = idf[index] * weighted_frequency
            tf_idf_list_doc.append(tf_idf)

        # document tf-idf normalization
        length = np.sqrt(np.sum(np.square(np.array(tf_idf_list_doc))))
        if length > 0:
            document_normalized[doc] = [round((x / length), 3) if x > 0 else 0 for x in tf_idf_list_doc]
        else:
            document_normalized[doc] = [0 for x in tf_idf_list_doc]
    return document_normalized


def normalize_query(query, idf):

    tf_idf_list = []
    query_normalized = []

    # calculate query tf-idf
    for word in query:
        index = query.index(word)
        frequency = query.count(word)
        weighted_frequency = math.log(frequency + 1)
        tf_idf = idf[index] * weighted_frequency
        tf_idf_list.append(tf_idf)
        l1 = np.sqrt(np.sum(np.square(np.array(tf_idf_list))))
        if l1 > 0:
            query_normalized = [round((x / l1), 3) for x in tf_idf_list]
        else:
            query_normalized = [0 for x in tf_idf_list]
    return query_normalized


def results_represent(document_index, tf_idf_values):

    authors = documents["authors_name"].iloc[document_index]
    if isinstance(authors, str):
        authors = authors.split(",")

    authors_links = documents["authors_links"].iloc[document_index]
    if isinstance(authors_links, str):
        authors_links = authors_links.split(",")

    year_of_publication = ""
    publication_date = documents["publication_date"].iloc[document_index]
    if isinstance(publication_date, str):
        year_of_publication = publication_date

    # format the output string
    output_string = f'Title: {documents["title"].iloc[document_index]}\n'
    output_string += f'Title Link: {documents["publication_link"].iloc[document_index]}\n'
    output_string += f'Authors: {", ".join(authors)}\n'
    output_string += f'Authors Link: {", ".join(authors_links)}\n'
    output_string += f'Year of Publication: {year_of_publication}\n'
    output_string += f'Abstract: {documents["abstract"].iloc[document_index]}\n'
    output_string += f'Normalized Tf-IDF score:{tf_idf_values}\n'

    '''dict_format = {'title': documents["title"].iloc[document_index],
                   "title_link": documents["publication_link"].iloc[document_index],
                   "authors": authors,
                   "authors_link": authors_links,
                   "year_of_publication": year_of_publication,
                   "abstract": documents["abstract"].iloc[document_index],
                   "Normalized Tf-IDF score": tf_idf_values
                   }'''
    return output_string


def search_query(query):

    global display_result
    global results_list

    # reading inverted index file from publication_index
    with open('output.txt', encoding="utf-8") as file:
        content = file.read()
        file.close()

    # checking the indexer for query processing
    inverted_index = ast.literal_eval(content)
    query_list = preprocessor_text(query)
    query_set = set(query_list)
    query_list = list(query_set)

    documents_set = set()
    idf_list = []

    # selecting each query word
    for word in query_list:

        if word in inverted_index:
            length = len(inverted_index[word])
            idf = math.log(len(inverted_index) / length)
            idf_list.append(idf)
            for i in inverted_index[word]:
                documents_set.add(i)
        else:
            idf_list.append(0)

    # normalizing tf-idf for both document and query
    document_vector = normalize_document(documents_set, query_list, idf_list)
    query_vector = normalize_query(query_list, idf_list)
    # Calculating the cosine similarity for the documents_pub
    cosine_similarity = {}

    for doc in document_vector:
        vector1 = np.array(document_vector[doc])
        vector2 = np.array(query_vector)
        vector = vector1 * vector2
        vector_product = np.sum(vector)
        cosine_similarity[doc] = vector_product

    answers = dict(sorted(cosine_similarity.items(), key=lambda x: x[1], reverse=True))
    # creating a list of results
    for answer in answers:
        tf_idf_values = {}
        for i, word in enumerate(query_list):
            tf_idf_values[word] = document_vector[answer][i]
            tf_idf_score = tf_idf_values[word]
        output = results_represent(answer, tf_idf_score)
        results_list.append(answer)
        display_result[answer] = output
        print(output)

query ="machinelearning"
search_query(query)