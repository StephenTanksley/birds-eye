import os
import json
import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv('../.env')

"""
    What do I even want to be doing in this module?
    I need to create a loader which will load new data into a database.
    To accomplish this, I need to:
    1) Read data from the most recent file.
    2) Populate the data to a dataframe
    3) Load data to database in a raw table.
        a. Load source data. This will need to happen only for as many sources as I have.
        b. Headline/link data. This will need to happen everyday. I'll need to develop a merge script for this.
        
"""


def read_json_from_directory(directory: str = "") -> list[str]:
    recents = max(os.listdir(directory))
    filepath = os.path.join(directory, recents)

    results = []
    with open(filepath, 'r') as file:
        all_records = json.load(file)
    for _, value in all_records.items():
        results.extend(value)

    return results



if __name__ == '__main__':
    pg_user = os.getenv('PGUSER', None)
    pg_password = os.getenv('PGPASSWORD', None)
    pg_port = os.getenv('PGPORT', None)
    pg_host = os.getenv('PGHOST', None)

    print(pg_user, pg_password, pg_port, pg_host)
    records = read_json_from_directory(directory="../data")

    df = pd.DataFrame(data=records)
    print(df.tail())
