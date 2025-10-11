import os
import json

"""
    What do I even want to be doing in this module?
    
    I need to create a loader which will load new data into a database.
"""

def read_json_from_directory(directory: str = ""):
    recents = max(os.listdir(directory))
    filepath = os.path.join(directory, recents)

    with open(filepath, 'r') as file:
        items = json.load(file)
        for item, value in items.items():
            print(item, '\n\t', value, '\n\n')

if __name__ == '__main__':
    read_json_from_directory(directory="../data")