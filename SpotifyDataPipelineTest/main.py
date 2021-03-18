import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "	31ufoecduolygedb6iqx7uuy7zfe"
TOKEN = "BQBtnijjJiae_PS8k8J4rHw65l7vDkms0DykY8kaHTN1hk3KXb37IYKlmLbVedzp7vonUK_l-RVyQFOUutNjFxdUsLHjfeFGYWJnNn21_BoHWywFiz6-KbQpK_k0JaA5VlRJn-fgSrb_AlsF70un3C99JZ8Hk46y6rrx7O3U"

# Generate your token here: https://developer.spotify.com/console/get-recently-played/
# Note: Need to login to Spotify

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if DataFrame is empty
    if df.empty:
        print("No song downloaded, Finishing Exeution")
        return False

    # Primary Key (played_at column) Check
    if pd.Series(df["played_at"]).is_unique:
        pass
    else:
        raise Exception("Primary key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null valued found")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned songs doesn't come from within the last 24 hours")
    
    return True

if __name__ == "__main__":

    # Extract part of the ETL process

    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=9&after={time}".format(time=yesterday_unix_timestamp), headers = headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name" : song_names,
        "artist_name" : artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])

    # Validate
    print(song_df)
    if check_if_valid_data(song_df):
        print("Data valid, proceed to load stage..")