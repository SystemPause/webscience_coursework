import pymongo
from pymongo import MongoClient
from datetime import datetime
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

"""
author: Alessandro Speggiorin
studentID: 2268690S

File containing helper functions used in different parts of the coursework

"""

# Custom function used to store tweets inside the database
# The function expects the tweet in a json format
def insert_tweet_db(json_data):
    # Connect to the local Mongo DB
    client = MongoClient()

    # Use a custom database called twitterDB. If it does not exist
    # it will be created
    db = client.twitterDB

    # Format the date format in a format compatible with MongoDB
    format_created_at = datetime.strptime(json_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    json_data['created_at'] = format_created_at

    #print("Tweet collected at " + str(json_data['created_at']))

    # Insert data in MONGODB
    db["twitterCollection"].insert_one(json_data)


# Helper function used to clean tweets text
# Reference used https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
def clean_tweet(tweet): 
    # Remove the RT text from each tweet. 
    if "RT" in tweet:
        tweet = tweet.replace("RT", "")
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
    

# Helper function used to convert tweets into frames 
def convert_tweet_to_frame(tweets):
    dataFrame = pd.DataFrame()
    # Tweets info
    dataFrame['_id'] = np.array([tweet['_id'] for tweet in tweets])
    dataFrame['text'] = np.array([tweet['text'] for tweet in tweets])
    dataFrame['text_len'] = np.array([len(tweet['text']) for tweet in tweets])
    dataFrame['created_at'] = np.array([tweet["created_at"] for tweet in tweets])
    dataFrame['source'] = np.array([tweet["source"] for tweet in tweets])
    
    dataFrame['likes'] = np.array([tweet["favorite_count"] for tweet in tweets])
    dataFrame['retweets'] = np.array([tweet["retweet_count"] for tweet in tweets])
    dataFrame['hashtags'] = np.array([[el['text'] for el in tweet['entities']['hashtags']] for tweet in tweets])
    
    # Replies info 
    dataFrame['in_reply_to_screen_name'] = np.array(list(tweet['in_reply_to_screen_name'] for tweet in tweets))
    dataFrame['in_reply_to_status_id_str'] = np.array(list(tweet['in_reply_to_status_id_str'] for tweet in tweets))
    dataFrame['in_reply_to_user_id_str'] = np.array(list(tweet['in_reply_to_user_id_str'] for tweet in tweets))
    dataFrame['is_quote_status'] = np.array(list(tweet['is_quote_status'] for tweet in tweets))
    
    # Retweeted info
    dataFrame['retweeted_screen_name'] = np.array([tweet['retweeted_status']['user']['screen_name'] if "retweeted_status" in tweet else None for tweet in tweets])
    dataFrame['retweeted_id'] = np.array([tweet['retweeted_status']['user']['id_str'] if "retweeted_status" in tweet else None for tweet in tweets])
    dataFrame['retweeted'] = np.array([tweet['retweeted'] for tweet in tweets])
    
    # Getting user mentions information
    dataFrame['user_mentions_screen_name'] = np.array([[el['screen_name'] for el in tweet['entities']['user_mentions']] for tweet in tweets])
    dataFrame['user_mentions_id'] = np.array([[el['id_str'] for el in tweet['entities']['user_mentions']] for tweet in tweets])

    # Original Author info
    dataFrame['user_screen_name'] = np.array([tweet["user"]['screen_name'] for tweet in tweets])
    dataFrame['user_id_str'] = np.array([tweet["user"]['id_str'] for tweet in tweets])
    dataFrame['user_followers_no'] = np.array([tweet["user"]['followers_count'] for tweet in tweets])
    

    return dataFrame


# Resource used https://github.com/ugis22/analysing_twitter/blob/master/Jupyter%20Notebook%20files/Interaction%20Network.ipynb
# Get the interactions between the different users
def get_interactions_set(row, reply=False, retweet=False, mention=False):
    # From every row of the original dataframe
    # First we obtain the 'user_id' and 'screen_name'
    user = row["user_id_str"], row["user_screen_name"]
    # If there is no user then return None
    if user[0] is None:
        return (None, None), []
    
    # Create a set for all interactions. 
    interactions = set()
    
    # Check if tweets are reply, retweet or mentions
    if reply: 
        # Add the interaction for replies
        interactions.add((row["in_reply_to_user_id_str"], row["in_reply_to_screen_name"]))
    if retweet:
        # Add the interaction for retweets
        interactions.add((row["retweeted_id"], row["retweeted_screen_name"]))
    if mention:
        # Add the interaction for mentions
        for mention_id, mention_screen_name in zip(row["user_mentions_id"], row["user_mentions_screen_name"]):
            interactions.add((mention_id,mention_screen_name ))
    
    # Discard if user id is in interactions
    interactions.discard((row["user_id_str"], row["user_screen_name"]))
    
    # Remove all empty interactions
    interactions.discard((None, None))
    return user, interactions


# Function used in order to get all user interactions. 
# The function returns a graph object and a dictionary representing all interactions
# between users
def get_users_interactions(df, graph, reply=False, retweet=False, mention=False):
    iteractions_dict = {}
    # For each row in our dataframe
    for index, tweet in df.iterrows():
        # get the interactions with that specific tweet
        user, interactions = get_interactions_set(tweet,reply, retweet, mention)
        # get the current user_id and screen_name
        user_id, user_name = user
        # For each of the possible interactions
        for interaction in interactions:
            iteractions_dict[user_name] = {}
            int_id, int_name = interaction
            # Add an edge from the user that posted the tweet to all other users that 
            # interacted somehow with the tweet
            graph.add_edges_from([(user_name,int_name)])

            # Keep a counter to see how users interacted
            if int_name in iteractions_dict[user_name]:
                iteractions_dict[user_name][int_name] += 1
            else:
                iteractions_dict[user_name][int_name] = 1
    return graph, iteractions_dict


# Function used to generate a graph and plot it if necessary
# The function returns a dictionary mapping each cluster
# to its relative graph and the dictionary of all interactions
def generate_network(clusters_dict, reply=False, retweet=False, mention=False, plot=False, label=None):
    results_dict = {}
    # For each cluster (including the general dataframe)
    print(f"Processing {label}")
    for key, value in clusters_dict.items():
        print(key)
        results_dict[key] = {}
        graph = nx.DiGraph()
        graph, iteractions_dict = get_users_interactions(value, graph, reply=reply, retweet=retweet, mention=mention)
        results_dict[key]["graph"] = graph
        results_dict[key]["interactions_dict"] = iteractions_dict
        
        # Get the graph's degree to see if there are actually nodes
        degrees = [val for (node, val) in graph.degree()]
        # If the degree is 0 then just assign the graph to be empty
        if len(degrees) == 0:
            results_dict[key]["graph"] = None
        # Otherwise plot it if the flag has been defined
        if len(degrees) > 0 and plot: 
            # Plot the graph
            pos = nx.spring_layout(graph, k=0.05)
            try:
                plt.figure(figsize = (5,5))
                nx.draw(graph, pos=pos, node_color=range(graph.number_of_nodes()), cmap=plt.cm.PiYG, edge_color="black", linewidths=0.3, node_size=60, alpha=0.6, with_labels=False)
                nx.draw_networkx_nodes(graph, pos=pos, node_size=300, node_color=colors_central_nodes)
                #plt.show()
            except:
                plt.savefig(f'{label}_{key}_reply_{reply}_retweet_{retweet}_mention_{mention}.png')
                pass
            print("================")
        else:
            print("Graph has degree less equal to 0 or the flag plot=False")
            print("================")
    return results_dict

# Resource used https://github.com/ugis22/analysing_twitter/blob/master/Jupyter%20Notebook%20files/Interaction%20Network.ipynb
# Get the interactions between the different hashtags
# The function returns a dictionary mapping hashtact relations
def get_hashtags_iter(df):
    hastags_dict = {}
    # For each row in the dataframe
    for index, row in df.iterrows():
        # Get each hashtags
        for hashtag in row['hashtags']:
            # If there are hashtags save their interaction as a set
            if hashtag not in hastags_dict:
                hastags_dict[hashtag] = set(row['hashtags'])
            else:
                hastags_dict[hashtag] = hastags_dict[hashtag].union(row['hashtags'])
            # Remove itself from the set
            hastags_dict[hashtag].remove(hashtag)
    
    # Remove every hashtag with no interaction
    final_dict = {}
    for key, value in hastags_dict.items():
        if len(value) != 0:
            final_dict[key] = value
    
    return final_dict 


# Function used to analyse graphs
def analyse_graph(graph, triads=False):
    if graph is not None:
        print(f"There are {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges present in the Graph")

        degrees = np.array([val for (node, val) in graph.degree()])
        node_values = np.array([node for (node, val) in graph.degree()])
        vip = node_values[np.argmax(degrees)]
        # Get top nodes
        sorted_nodes = node_values[np.argsort(degrees)][::-1]

        print(f"The average degree of the nodes in the Graph is {np.mean(degrees):.1f}") 
        print(f"The maximum degree of the Graph is {np.max(degrees)}") 
        print(f"The node with maximum degree is {sorted_nodes[0]}")
        print(f"The top 5 nodes are {sorted_nodes[:5]}")

        # Compute and print triads
        if triads:
            print("Triads")
            print(nx.algorithms.triads.triadic_census(graph))
    else:
        print("Empty")
    print("=======")
    