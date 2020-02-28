import access_keys
import tweepy
import pymongo
from pymongo import MongoClient
import json 
from datetime import datetime
import pprint as pp
from helper_functions import *


"""
author: Alessandro Speggiorin
studentID: 2268690S

[Total 15 marks] Develop a crawler to access as much Twitter data as possible.
a. [5 marks] Use Twitter streaming API for collecting 1% data.

"""



# Implement custom StreamListener
class StreamListener(tweepy.StreamListener):    
        
    def on_connect(self):
        print("Connected to the streaming API")
        print("Downloading data...")
 
    def on_error(self, status_code):
        # Print an error message and the relative error code if an error occurs
        print('An error has occured. Status Code: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        try:
            insert_tweet_db(json.loads(data))
            return
        except Exception as error:
            print(error)
            pass


if __name__ == "__main__":
    print(("="*40) + "QUESTION 1A " + ("="*40))
    # Create the api object reference
    api=tweepy.API(access_keys.auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True,parser=tweepy.parsers.JSONParser())

    # Run the streaming API. Specify the collection we want to use 
    # and start the stream. Filter tweets by considering only english tweets that are 
    # UK based. 
    streamListener = StreamListener()
    customStream = tweepy.Stream(auth = api.auth, listener=streamListener)
    customStream.filter(languages=['en'],locations=[-7.57216793459, 49.959999905, 1.68153079591, 58.6350001085], is_async=True)
