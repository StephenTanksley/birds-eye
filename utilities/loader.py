import os
import json

def load():
    for file in os.listdir('../data'):
        if file.endswith('.json'):
            print(file)


if __name__ == '__main__':
    load()