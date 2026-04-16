import os
import json
from collections import Counter
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from nltk.util import bigrams
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import sqlalchemy as sa


# This is going to be the counter for words on a per-source basis.
def construct_topic_counter(value_list: list[str] = None):

    keywords_list = [value_item.get("keywords") for value_item in value_list if len(value_item.get("keywords")) > 2]

    flattened_list = [value_item for sublist in keywords_list for value_item in sublist]
    topics_counter = Counter(flattened_list)
    return topics_counter


# This is going to be the counter for words on a per-source basis.
def construct_topic_list(value_list: list[str] = None):
    keywords_list = [item.get("keywords") for item in value_list if len(item.get("keywords")) > 2]
    return keywords_list


if __name__ == '__main__':
    file_path = "/home/stephen-tanksley/Documents/CODE/Python_Projects/birds-eye/data/"
    latest_item_path = os.path.join(file_path, max(os.listdir(file_path)))
    with open(latest_item_path, 'r') as file:
        data = json.load(file)

    collection = []
    strings = []
    counter = Counter()
    # count_vectorizer = CountVectorizer(encoding='utf-8')
    for key, value in data.items():
        if value is []:
            continue
        collection.extend(construct_topic_list(value_list=value))
        counter = counter + construct_topic_counter(value_list=value)


    for item in collection:
        strings.append(' '.join([sub_item for sub_item in item]))

    # print(counter)
    # count_vectorizer = CountVectorizer(ngram_range=(1, 3), encoding='utf-8')
    # count_vectorizer.fit_transform(strings)
    #
    # feature_names = count_vectorizer.get_feature_names_out()

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counter)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'News Topics by Keyword Frequency')
    plt.show()
