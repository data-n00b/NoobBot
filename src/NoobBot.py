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
#from geopy.geocoders import Nominatim
import pandas as pd
import datetime
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
import numpy as np
 
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
       
    
    def calculateScore(self,twitterDF):
        self.twitterDF = twitterDF
        self.twitterDF['cVerified'] = [2 if i == True else 1 for i in self.twitterDF['Is Verified']]
        self.twitterDF['rawImpactScore'] = (self.twitterDF['Retweet Count'] + self.twitterDF['Favorite Count'] + (self.twitterDF['Followers Count']*self.twitterDF['cVerified']) )*self.twitterDF['Sentiment Polarity']
        self.twitterDF['nImpactScore'] = 0
        #Dropping Tweets that have neutral polarity
        self.twitterDF = self.twitterDF[self.twitterDF['rawImpactScore'] != 0]
        #Splitting into groups of Positive and negative raw impact.
        self.twitterDFP = self.twitterDF[self.twitterDF['rawImpactScore'] > 0]
        self.twitterDFN = self.twitterDF[self.twitterDF['rawImpactScore'] < 0]
        #self.up = 100
        #self.low = -100
        self.groupedP = self.twitterDFP.groupby('Search Term')        
        for name, group in self.groupedP:
            self.up = 100
            self.low = 1
            self.maxImpact = max(group['rawImpactScore'])
            self.minImpact = min(group['rawImpactScore'])
            print(name,self.minImpact,self.maxImpact)
            self.twitterDFP['nImpactScore'] = ((((self.up)-(self.low)) * (self.twitterDFP['rawImpactScore']- (self.minImpact))) / ((self.maxImpact) - (self.minImpact))) + (self.low)
        self.groupedN = self.twitterDFN.groupby('Search Term')
        for name, group in self.groupedN:
            self.up = -1
            self.low = -100
            self.maxImpact = max(group['rawImpactScore'])
            self.minImpact = min(group['rawImpactScore'])
            print(name,self.minImpact,self.maxImpact)
            self.twitterDFN['nImpactScore'] = ((((self.up)-(self.low)) * (self.twitterDFN['rawImpactScore']- (self.minImpact))) / ((self.maxImpact) - (self.minImpact))) + (self.low)  
        self.twitterDF = pd.concat([self.twitterDFP,self.twitterDFN],axis = 0, ignore_index = True)
        self.twitterDF = self.twitterDF.drop(['Tweet ID', 'cVerified'],axis=1)
        return self.twitterDF

#Defining Tweet Scraper as a separate function outside the scope of the class
def tweetScraper(bot,trendsList,forTime=15,onceEvery=60,filename = (datetime.datetime.now().strftime('%m_%d_%Y') + ' tweetDump.csv')):
    '''
    bot - api authenticated Tweepy Object
    forTime - Time limit in minutes to scrape tweets for.
    onceEvery - Time in seconds that the scrapper sleeps and wakes.
    trendsList - List of Trends from an object or custom trends to search for. Must be a list object
    writes to an output CSV file
    '''
    t_end = time.time() + onceEvery*forTime
    tListAll = []
    while time.time() < t_end:
        for i in range(len(trendsList)):
            tListAll = (bot1.searchTweets(trendsList[i])[0])
        time.sleep(onceEvery)
        print('End of sleep')
    with open(filename,'a',encoding="UTF8") as file:
        tListAll.to_csv(file,header=True)
    print('Finished Scraping')
    return tListAll

def getLocation(locString):
    """
    Method to get the name or location of the closest match
    and return the weoid from the json
    """
class predictImpact(object):
    def __init__(self,trainData,predictData):
        self.trainData = trainData
        self.predictData = predictData
        self.features =['Search Term','Retweeted','Retweet Count','Favorite Count']
    
    def encodeModel(self,inData):
        self.inData = inData
        X = self.inData[self.features]
        encodedPredictors = pd.get_dummies(X)
        return encodedPredictors
    
    def buildModel(self):
        self.inData = self.encodeModel(self.trainData)
        self.y = self.trainData.nImpactScore
        train_X,val_X,train_y,val_y = train_test_split(self.inData,self.y,random_state = 42)
        #Specify Model
        self.tweetModel = DecisionTreeRegressor(random_state = 42)
        #Fit Model
        self.tweetModel.fit(train_X,train_y)
        return self.tweetModel
    
    def modelPredict(self):
        self.inData = self.encodeModel(self.predictData)
        self.y = self.predictData.nImpactScore
        self.val_predictions = self.tweetModel.predict(self.inData)
        return self.val_predictions


if __name__ == '__main__':

    '''
    consumer_key = '<Your Consumer Key>'; 
    consumer_secret = '<Your Consumer Secret>'; 
    access_token = '<Your Access token>'; 
    access_token_secret = '<Your Access Token Secret>';
    '''

    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth)
    
    bot1 = NoobBot(api)
    trendsList = bot1.locTrends()
    tListAll = tweetScraper(bot1,trendsList)
    #print('Finished Scraping')
    #tListAll = pd.read_csv(r"C:\Users\Arvind\OneDrive\Data Backup Folder From Dell\Documents\NC State\Fall 2018\ISE 589 Python\Project\scrapedData_11_05_extended.csv")
    tListImpact = bot1.calculateScore(tListAll)
    predictData = tweetScraper(bot1,trendsList,forTime=1,filename='predictors.csv')
    newP =predictData.drop(['Tweet ID','Created At','Tweet Text','Followers Count','User Handle','Sentiment Polarity'],axis = 1)    #testKeywords = pd.read_csv(r"C:\Users\Arvind\OneDrive\Data Backup Folder From Dell\Documents\NC State\Fall 2018\ISE 589 Python\Project\testSentiment.csv")
    newP['nImpactScore'] = ""
    mlObject = predictImpact(tListImpact,newP)
    mlObject.buildModel()
    x = mlObject.modelPredict()    
    newP['nImpactScore'] = x
    print(newP.head(10))