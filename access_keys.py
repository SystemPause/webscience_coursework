import tweepy

"""
author: Alessandro Speggiorin
studentID: 2268690S

In this files there are all solutions for question 2-3-4 

"""

# Twitter Access Details
CONSUMER_KEY = 'sPTfr4cCAh09JrBijhDbdLUDd'
CONSUMER_SECRET ='1BKo0hEUdDTd8GLHDmqiwW8mNuTdgFCn93S5vMolTCCIdEb5VH'
ACCESS_TOKEN ='3910851693-uyVpoaDuACfypLQEuNyniAljLHNI9xcJxn24mvS'
ACCESS_TOKEN_SECRET ='YvkddqNpWtgdgb1DfoBlU8jejOC83oFsqWi1tOzx08b9W'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET) 
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

UPLOAD_DATA_FROM_FILE = False