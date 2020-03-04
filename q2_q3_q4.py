import pymongo
from pymongo import MongoClient
from helper_functions import *
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import pandas as pd
import pprint as pp
import networkx as nx
import access_keys
from bson import json_util


"""
author: Alessandro Speggiorin
studentID: 2268690S

In this files there are all solutions for question 2-3-4 

"""

if __name__ == "__main__":
    # 2) [25 marks] Grouping of tweets: Group the tweets based on content analysis, You can
    #    collect the data and then cluster them using any off-the shelf software; or use any
    #    locality sensitive hashing software; or build a content index and group them (for
    #    example, http://bonsai.hgc.jp/~mdehoon/software/cluster/software.html

    # c. Describe your method for grouping. What software you used and how the
    #    groups are formed. [5 marks]

    #    For grouping I've used k-means clustering with a TFIDF vectoriser in order
    #    to group  togheter similar tweets based on their content (after cleaning them).
    #    I've also used the elbow-method in order to find the optimal value of cluster which
    #    in our case is 5. The reference I've used is the following https://heartbeat.fritz.ai/k-means-clustering-using-sklearn-and-python-4a054d67b187 
    print(("="*40) + "QUESTION 2C " + ("="*40))
    # Get all data from the DB
    client = MongoClient()
    db = client.twitterDB

    # If the flat UPLOAD_DATA_FROM_FILE is set the try to load and save file in mongoDB
    if access_keys.UPLOAD_DATA_FROM_FILE:
        with open('sampleData.json') as f:
            file_data = json_util.loads(f.read())
        # Delete whatever is already in the collection and overwrite with what in the file
        db["twitterCollection"].drop()
        db["twitterCollection"].insert_many(file_data)

    # Load all tweets from the DB
    tweets = db.twitterCollection.find()

    # Clean tweet texts
    tweets_list = []
    for tweet in tweets:
        tweet['text'] = clean_tweet(tweet['text'])
        tweets_list.append(tweet)

    # Convert twitters to a pandas dataframe
    twitter_df = convert_tweet_to_frame(tweets_list)
    # Remove duplicates
    twitter_df.drop_duplicates(subset ="_id",keep = False, inplace = True) 
    print(twitter_df)

    # Create the tfidfVectoriser and fit_transform it by using tweets text
    tfidf_vect = TfidfVectorizer(stop_words="english") 
    training_set = tfidf_vect.fit_transform(twitter_df["text"])

    # use the elbow method to find best k value
    print("Finding best k value and saving the graph")
    loss =[]
    for i in range(1, 7):
        kmeans = KMeans(n_clusters = i).fit(training_set)
        kmeans.fit(training_set)
        loss.append(kmeans.inertia_)

    plt.plot(range(1, 7), loss)
    plt.title('Elbow method')
    plt.xlabel('No of clusters')
    plt.ylabel('Loss')
    plt.savefig("elbom_method.png")
    #plt.show()
    print("Elbow method file saved")

    # The best value for K would be 5
    # Compute kmeans
    K_means = KMeans(n_clusters=5)
    K_means.fit(training_set)

    # Assign those cluster back to the dataset
    twitter_df['cluster_label'] = K_means.labels_.tolist()

    # Extract dataframes for each cluster
    cluster0 = twitter_df[twitter_df['cluster_label'] == 0]
    cluster1 = twitter_df[twitter_df['cluster_label'] == 1]
    cluster2 = twitter_df[twitter_df['cluster_label'] == 2]
    cluster3 = twitter_df[twitter_df['cluster_label'] == 3]
    cluster4 = twitter_df[twitter_df['cluster_label'] == 4]

    clusters_list = [cluster0, cluster1, cluster2, cluster3, cluster4]

    # i. Extract important usernames; hashtags and entities/concepts from the
    #    group. The idea here is to describe the strategy you used . [10 marks]
    print(("="*40) + "QUESTION 2Ci " + ("="*40))
    # Extract Important hashtags using a simple dictionary
    top_hashtags = {}
    for i in range(len(clusters_list)):
        top_hashtags["cluster" + str(i)] = {}
        for hashtag_list in clusters_list[i]['hashtags']:
            for hashtag in hashtag_list:
                if hashtag in top_hashtags["cluster" + str(i)]:
                    top_hashtags["cluster" + str(i)][hashtag] += 1
                else:
                    top_hashtags["cluster" + str(i)][hashtag] = 1
                
    # Print results
    print("Printing top hashtags for each cluster:")
    for el in top_hashtags:
        sorted_dict_items = list({k: v for k, v in sorted(top_hashtags[el].items(), key=lambda item: item[1], reverse=True)}.items())
        # Print top 3 values
        sorted_dict_items = sorted_dict_items[:3]
        print(el)
        print("=====")
        
        if len(sorted_dict_items) > 0:
            for el in sorted_dict_items:
                print(el[0] + ":" + str(el[1]))
        else:
            print("No hashtags")
        print("=====")
    print("Done printing hashtags")

    # Extract Important mentions
    print("Printing top metnions for each cluster:")
    top_mentions = {}
    for i in range(len(clusters_list)):
        top_mentions["cluster" + str(i)] = {}
        for mention_list in clusters_list[i]['user_mentions_screen_name']:
            for mention in mention_list:
                if mention in top_mentions["cluster" + str(i)]:
                    top_mentions["cluster" + str(i)][mention] += 1
                else:
                    top_mentions["cluster" + str(i)][mention] = 1
    # Print results
    for el in top_mentions:
        sorted_dict_items = list({k: v for k, v in sorted(top_mentions[el].items(), key=lambda item: item[1], reverse=True)}.items())
        # Print top 3 values
        sorted_dict_items = sorted_dict_items[:3]
        print(el)
        print("=====")
        
        if len(sorted_dict_items) > 0:
            for el in sorted_dict_items:
                print(el[0] + ":" + str(el[1]))
        else:
            print("No mentions")
        print("=====")
    print("Done printing mentions")

    # ii. Provide statistics on the data collected (part 1) and the resulting groups
    #     (grouped data) [10]

    #     There are different statistics that can be taken into account for this task. Possible ones are
    #         Total number of elements per cluster
    #         Average tweets lenght
    #         Average likes
    #         Average retweets
    print(("="*40) + "QUESTION 2Cii " + ("="*40))
    # Add also the original dataset to the list of clusters
    clusters_dict = {"cluster0": cluster0, 
                    "cluster1": cluster1,
                    "cluster2": cluster2,
                    "cluster3": cluster3,
                    "cluster4": cluster4,
                    "Original Dataframe": twitter_df}

    # Number of elements in each cluster
    for key, value in clusters_dict.items():
        print(key  + " has " + str(value.shape[0])  + " elements")

    # Print average tweets length
    for key, value in clusters_dict.items():
        print(key  + " has an average tweet length equal to " + str(value.mean()['text_len']))

    # Print average number of likes
    for key, value in clusters_dict.items():
        print(key  + " has an average number of likes equal to " + str(value.mean()['likes']))

    # Print average number of retweets
    for key, value in clusters_dict.items():
        print(key  + " has an average number of retweets equal to " + str(value.mean()['retweets']))


    # 3) [25 marks] Capturing & Organising User and hashtag information through a user
    #               interaction graph. First focus on user mentions and then on hashtags.

    # a. [15 marks] Develop a method to capture user information. Users occurring
    #               together in general data as well as on the groups (groups you formed in part
    #               2 above) Differentiate between different kinds of networks like retweet
    #               network; quote tweets etc.

    print(("="*40) + "QUESTION 3A " + ("="*40))
    # With mentions
    users_mentions = generate_network(clusters_dict, reply=False, retweet=False, mention=True, plot=False, label="mentions")
    # Only retweets
    users_retweets = generate_network(clusters_dict, reply=False, retweet=True, mention=False, plot=False, label="retweets")
    # Only replies 
    users_replies = generate_network(clusters_dict, reply=True, retweet=False, mention=False, plot=False, label="replies")

    # Show the user dictionary as a reference for cluster 0 
    print("Example data structure for user interactions for cluster0")
    pp.pprint(users_mentions['cluster0']['interactions_dict'])
    
    # b. [10 marks] Develop a mechanism to capture hashtag information occurring
    #               together in general data as well as on the groups. Objective is to build a user
    #               interaction graph through hashtag co-occurring information. (frequency
    #               doesn’t make such in this case)
        
    print(("="*40) + "QUESTION 3B " + ("="*40))
    hashtags_dict = {}
    # Plot a graph for each cluster considering hashtags
    for key, value in clusters_dict.items():
        hashtags_dict[key] = {}
        # Map the interaction to the dictionary
        hashtags_dict[key]['interactions_dict'] = get_hashtags_iter(value)
        print(key + " has " + str(len(hashtags_dict[key]['interactions_dict'])) + " hashtags")
        graph = nx.Graph()
        
        # Add edges based on hashtags interactions
        for from_node, to_node in hashtags_dict[key]['interactions_dict'].items():
            for el in to_node: 
                graph.add_edge(from_node, el)
        
        # Save the graph for this specific hashtags interaction in the dictionary. None if the graph is empty
        degrees = [val for (node, val) in graph.degree()]
        hashtags_dict[key]['graph'] = graph if len(degrees) > 0 else None
        
        if len(degrees) >0: 
                pos = nx.spring_layout(graph, k=0.05)
                try:
                    plt.figure(figsize = (5,5))
                    nx.draw(graph, pos=pos, node_color=range(graph.number_of_nodes()), cmap=plt.cm.PiYG, edge_color="black", linewidths=0.3, node_size=60, alpha=0.6, with_labels=False)
                    nx.draw_networkx_nodes(graph, pos=pos, node_size=300, node_color=colors_central_nodes)
                    plt.show()
                except:
                    plt.savefig(f'hashtags_{key}.png')
                    pass
                print("================")
        else:
            print("Network Not defined")

    
    # print the hashtag datastructure for cluster0
    print("Example data structure for hashtags interactions for cluster0")
    pp.pprint(hashtags_dict['cluster0']['interactions_dict'])

    # 4. [25 marks] Network Analysis
    # a. Analyse the data to generate network-based measures like ties, triads.
    print(("="*40) + "QUESTION 4A " + ("="*40))
    # Analyse user mentions
    print("Analysing users mentions graph")
    for key, value in users_mentions.items():
        print(key)
        analyse_graph(value['graph'], True)

    # Analise network with retweets
    print("Analysing users retweets graph")
    for key, value in users_retweets.items():
        print(key)
        analyse_graph(value['graph'], True)

    # Analise network with replies
    print("Analysing users replies graph")
    for key, value in users_replies.items():
        print(key)
        analyse_graph(value['graph'], True)

    # Analise network with hashtags
    print("Analysing hashtags graph")
    for key, value in hashtags_dict.items():
        print(key)
        analyse_graph(value['graph'], False)
        
        
                
        
            
                
                    