import tweepy 
import time
import access_keys
from helper_functions import *


"""
author: Alessandro Speggiorin
studentID: 2268690S

In this files there is the solution for question 1

"""

# Helper function used in order to get tweets by using the rest API 
def get_tweets_rest(key_words, api, n_items=1000, schedule=False):
    print(f"Collecting {n_items} tweets")
    # Chain the key_words for search 
    key_words_string = " OR ".join(key_words)

    cursor = tweepy.Cursor(api.search, q = key_words_string, lang = "en").items(n_items)
    while True:
        try:
            status = cursor.next()
            # Insert into db
            try:
                insert_tweet_db(status._json)
            except:
                # If an error occurs when trying to insert 
                # into the DB continue
                continue
        except tweepy.TweepError:
            time.sleep(60 * 15)
            continue
        except StopIteration:
            break
    print("Done collecting tweets")

if __name__ == "__main__":
    print(("="*40) + "QUESTION 1B " + ("="*40))
    # Create the api object reference
    api=tweepy.API(access_keys.auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

    world_trends = api.trends_available()
    # Find the United Kingdom WOEID
    UK_woeid = ""
    for world_trend in world_trends:
        if "name" in world_trend:
            if world_trend["name"] == "United Kingdom":
                UK_woeid = world_trend["woeid"]
                break
    
    print("==============")
    print("United Kingdom woeid: " + str(UK_woeid))
    print("==============")
    # Get all the top trends in the united states
    UK_trends_list = api.trends_place(id = UK_woeid)[0]['trends']
    # Extract only the trends names. We are interested in the keywords. 
    UK_trends = [UK_trend['name'] for UK_trend in UK_trends_list]
    print("List of top trends in UK")
    print(UK_trends)
    print("==============")




    # Pass the top 5 trends. Tried with 10 but apparently there is a limit in the number of tweets that can be passed
    get_tweets_rest(UK_trends[:5], api)