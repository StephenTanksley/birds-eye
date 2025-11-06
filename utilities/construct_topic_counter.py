import os
import json
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import sqlalchemy as sa



# This is going to be the counter for words on a per-source basis.
def construct_topic_counter(value_list: list[str] = None):

    keywords_list = [item.get("keywords") for item in value_list if len(item.get("keywords")) > 2]

    flattened_list = [item for sublist in keywords_list for item in sublist]
    topics_counter = Counter(flattened_list)
    return topics_counter

if __name__ == '__main__':
    file_path = "/home/stephen-tanksley/Documents/CODE/Python_Projects/birds-eye/data/"
    latest_item_path = os.path.join(file_path, max(os.listdir(file_path)))
    with open(latest_item_path, 'r') as file:
        data = json.load(file)

    counter = Counter()
    for key, value in data.items():
        new_counter = construct_topic_counter(value_list=value)
        counter = counter + new_counter

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counter)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'News Topics by Keyword Frequency')
    plt.show()
