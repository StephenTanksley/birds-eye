import os
import sys
import json
import spacy
from spacy import displacy


def recognize_keywords(keyword_list: str = None):
    nlp = spacy.load('en_core_web_sm')

    if keyword_list is None:
        return

    # sentence = " ".join(keyword_list)
    sentence = keyword_list
    doc = nlp(sentence)
    return doc

if __name__ == '__main__':
    file_path = "/home/stephen-tanksley/Documents/CODE/Python_Projects/birds-eye/data/"
    latest_item_path = os.path.join(file_path, max(os.listdir(file_path)))
    with open(latest_item_path, 'r') as file:
        data = json.load(file)

    values = [item for item in data.items()]

    results = []
    for item in values:
        unpacked = item[-1]

        for result in unpacked:
            if len(result) > 0:
                results.append(result.get('headline'))

    dates = []
    ordinals = []
    orgs = []
    persons = []
    places = []
    products = []
    times = []
    misc = []

    sort_bucket = {
        'DATE': dates,
        'ORDINAL': ordinals,
        'ORG': orgs,
        'PERSON': persons,
        'LOC': places,
        'PRODUCT': products,
        'TIME': times
    }

    for item in results:
        processed_keywords = recognize_keywords(item)

        for ent in processed_keywords.ents:
            print(ent)
            bucket = sort_bucket.get(ent.label_, misc)
            bucket.append(ent)

    for key, value in sort_bucket.items():
        print(key)
        print('\t', value)


    # print("Orgs: ", orgs)
    # print("Persons: ", persons)
    # print("Products: ", products)
    # print("Places: ", places)
    # print("Times: ", times)

"""
    Use AI for reading comprehension. Use AI as a witness, not as a judge.
    Use supabase for managed Postgres.
    Huggingface Spaces - very easy to 

"""