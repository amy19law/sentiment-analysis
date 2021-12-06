# Install Libraries/Dependencies
import numpy as np
import pandas as pd
import re

from textblob import TextBlob

from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import Credentials

# Twitter Authenticater
class Authenticator():
    # Read Twitter API Credentials from Separate File 
    def authenticate_credentials(self):
        authenticate = OAuthHandler(Credentials.consumer_key, Credentials.consumer_secret)
        authenticate.set_access_token(Credentials.access_token, Credentials.access_token_secret)
        
        return authenticate
    
    print("Credentials Authenticated")
    

# Twitter Client
class Client():
    # Set the Twitter User & Gain Access
    def __init__(self, twitterUser=None):
        self.auth = Authenticator().authenticate_credentials()
        self.twitterClient = API(self.auth)

        self.twitterUser = twitterUser

    def get_api(self):
        return self.twitterClient

# Twitter Streamer
class Streamer():
    print("Connecting to Twitter")
    
    # Class for Streaming & Processing Tweets.
    def __init__(self):
        self.twitter_autenticator = Authenticator()    

    def stream_tweet(self, getFilename, hashtags):
        # Handle Twitter Authetification & Connection to Twitter Streaming API
        listener = Listener(getFilename)
        authenticate = self.twitter_autenticator.authenticate_credentials() 
        stream = Stream(authenticate, listener)

        # Filter Twitter Streams to Capture Data
        stream.filter(track=hashtags)


# Twitter Stream Listener
class Listener(StreamListener):
    print("Gathering Tweets")
    
    # Listener to Print Received Tweets
    def __init__(self, getFilename):
        self.getFilename = getFilename

    def on_status(self, data):
        try:
            print(data)
            with open(self.getFilename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_status %s" % str(e))
        return True
          
    def on_error(self, status):
        if status == 420:
            # Return False on_status method if Rate Limit Occurs.
            return False
        print(status)

# Tweet Analyser
class TweetAnalyser():
    print("Analysing Tweets")
    
    # Analysing and Categorising Data from Tweets
    def clean_tweet_data(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    # Defining Result 1 = Positive, 0 = Neutral & -1 = Negative Sentiment
    def sentiment_analysis(self, tweet):
        analysis = TextBlob(self.clean_tweet_data(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    # Displaying Tweet - Using Numpy & Pandas 
    def data_frame(self, tweets):
        dataFrame = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        dataFrame['id'] = np.array([tweet.id for tweet in tweets])
        dataFrame['len'] = np.array([len(tweet.text) for tweet in tweets])
        dataFrame['date'] = np.array([tweet.created_at for tweet in tweets])
        dataFrame['source'] = np.array([tweet.source for tweet in tweets])
        dataFrame['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        dataFrame['likes'] = np.array([tweet.favorite_count for tweet in tweets])

        return dataFrame


if __name__ == '__main__':

    twitterClient = Client()
    tweetAnalyser = TweetAnalyser()

    # Twitter Topic to be Mined & Analysed
    api = twitterClient.get_api()
    tweets = api.search('Liverpool', count=200)
    print("Analysis Complete")
    
    # Display Sentiment Score
    dataFrame = tweetAnalyser.data_frame(tweets)
    dataFrame['sentiment'] = np.array([tweetAnalyser.sentiment_analysis(tweet) for tweet in dataFrame['tweets']])

    # Amount of Tweets to be Analysed & Displayed
    print(dataFrame.head(10))
