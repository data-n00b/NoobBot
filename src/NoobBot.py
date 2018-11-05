""" NOTES
Tweepy does not seem to handle the #Retweeted module very well. Doing an automatic search before putting into a dataFrame
Run once and check what the columns of the dataframe are.
You can probably drop the user handle.
Figure out a way to come up with an impact score.
Find good ways to plot.
Define inputs for the methods.
Figure out a way to create a way to have a test and training data set with and without the impact scores.
Iron out kinks with wherever the location information is called.
Write a better cleanText method. Current method seems to change the content.
Try to weed out duplicates or try to drop retweets all together.
Find a way to automatically run and scrape with a bash script.

DONE - Try to use time ticks to capture enough information. - Handled with the sleep module of time

CURRENT STATUS
Runs the code, takes top ten trends for New York, runs a search for 5 minutes
Updates content in a dataframe for all above obtained keywords and saves to a data frame.
Using a bash script to scrape data and shut down the computer.
"""
#---------------Importing Packages----------------------#
import tweepy
import json
import markovify
from textblob import TextBlob
import re
import time
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None
 
#geolocator = Nominatim(user_agent = "NoobBot")
#location = geolocator.geocode("Raleigh NC")
#print((location.latitude, location.longitude))
#---------------Initializing the Tweepy Object----------------------#

#tweept API is an autheticated tweepy object
class NoobBot(object):
    def __init__(self,tweepyAPI):
        self.tweepyOb = tweepyAPI
        self.tweets = []
#Location set to New York By default
#locTrends returns a list of trend names from the JSON object
    def locTrends(self, woeid = 2459115,numTrends = 10):
        self.trend =[]
        self.trendJSON = self.tweepyOb.trends_place(woeid)
        for i in range(numTrends):
            self.trend.append(self.trendJSON[0]['trends'][i]['name'])
        return self.trend
#searchTweets to search and return tweets within a location. Defaults to worldwide
#Have to figure out a way to limit duplicates.
#Maybe run it every hour or so.
    def searchTweets(self,searchQuery):
        #Search Quesry Loaded with defaults.
        self.termSearch = self.tweepyOb.search(searchQuery,lang='en',count = 100,show_user=False,result_type='mixed')
        #Retireving all tweets and marking reweets
        for tweet in self.termSearch:
            self.tweets.append([searchQuery,tweet.id,tweet.created_at,tweet.text,tweet.retweeted,tweet.retweet_count,tweet.favorite_count, tweet.user.followers_count,tweet.user.verified,tweet.user.screen_name,self.tweetSentiment(tweet.text)])
        for tweet in self.tweets:
            if tweet[3].startswith('RT '):
                tweet[4] = True
            tweet[3] = self.cleanTweet(tweet[3])
        self.colNames =['Search Term','Tweet ID','Created At','Tweet Text','Retweeted','Retweet Count','Favorite Count','Followers Count','Is Verified','User Handle','Sentiment Polarity']
        self.tweetDF = pd.DataFrame(self.tweets,columns = self.colNames)
        self.tweetDF = self.tweetDF.drop_duplicates()
        return  self.tweetDF,self.termSearch
#Clean Dataframe cleans the text in the tweets and returns a dataframe with the text, id and parameters    
    def cleanTweet(self,text):
        text = re.sub(r"RT ", "", text) #Strip RT at head
        text = re.sub(r"@\S+", "", text) #Strip first @mentions
        text = re.sub(r"http\S+", "", text) #Strip URLS
        text = re.sub('\W+', ' ', text) #Strip special characters
        text = re.sub(' +', ' ',text) #Strip un-caught white spaces
        return text
    
    def tweetSentiment(self,text):
        self.blob = TextBlob(text)
        return self.blob.sentiment.polarity
        
#def tweetScrape(bot,minutes=5,sleep = 1):
#    t_end = time.time() + 60*minutes
#    while time.time() < t_end:
#        tweetsList, tweetJSON = bot.searchTweets(trendsList[2])
#        time.sleep(sleep*60)
#    return tweetsList, tweetJSON
        
if __name__ == '__main__':
    consumer_key = '<Your Consumer Key>'; 
    consumer_secret = '<Your Consumer Secret>'; 
    access_token = '<Your Access token>'; 
    access_token_secret = '<Your Access Token Secret>';
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth)
    
    bot1 = NoobBot(api)
    trendsList = bot1.locTrends()
    #tweetsList, tweetJSON = bot1.searchTweets(trendsList[2])
    t_end = time.time() + 60*15
    tListAll = []
    while time.time() < t_end:
        for i in range(len(trendsList)):
            tListAll = (bot1.searchTweets(trendsList[i])[0])
        time.sleep(60)
    with open('scrapedData_11_05.csv','a',encoding="UTF8") as file:
        tListAll.to_csv(file,header=True)
    
