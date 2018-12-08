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
import pandas as pd
import datetime
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
import numpy as np

#---------------Initializing the Tweepy Object----------------------#

#tweept API is an autheticated tweepy object
class NoobBot(object):
    def __init__(self,tweepyAPI):
        self.tweepyOb = tweepyAPI
        self.tweets = []
#Location set to New York By default
#locTrends returns a list of trend names from the JSON object
    def locTrends(self, woeid = 1,numTrends = 10):
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
        self.tweetDF = self.tweetDF.drop_duplicates(subset='Tweet ID')
        self.tweetDF = self.tweetDF.drop_duplicates(subset='Tweet Text')
        return  self.tweetDF,self.termSearch
#Clean Dataframe cleans the text in the tweets and returns a dataframe with the text, id and parameters    
    def cleanTweet(self,text):
        text = re.sub(r"(?:\@|https?\://)\S+", "", text) #Strip @mentions and links.
        text = text.strip() #Strip trailing and beginning whitespaces
        text = " ".join(text.split()) #Handle any other whitespaces in the middle of the text
        return text
    
    def tweetSentiment(self,text):
        self.blob = TextBlob(text)
        return self.blob.sentiment.polarity
       
    
    def calculateScore(self,twitterDF):
        """
        Method to calculate raw and normalized impact scores.
        Input is a data frame object returned by the searchTweets method
        Tweets with 0 sentiment polarity are dropped since they do not contribute to the impact score.
        Data is normalized between -100 and 100
        """
        self.twitterDF = twitterDF
        self.twitterDF['cVerified'] = [2 if i == True else 1 for i in self.twitterDF['Is Verified']]
        self.twitterDF['rawImpactScore'] = (self.twitterDF['Retweet Count'] + self.twitterDF['Favorite Count'] + (self.twitterDF['Followers Count']*self.twitterDF['cVerified']))*self.twitterDF['Sentiment Polarity']
        self.twitterDF['nImpactScore'] = 0
        #Dropping Tweets that have neutral polarity        
        #Normalizing Impact score calculation by group
        self.twitterDF = self.twitterDF[self.twitterDF['rawImpactScore'] != 0]
        self.groupedAll = self.twitterDF.groupby('Search Term')        
        a = -1
        b = 1
        for name, group in self.groupedAll:
            maxR = max(group['rawImpactScore'])
            minR = min(group['rawImpactScore'])
            tempRaw = self.twitterDF['rawImpactScore'][self.twitterDF['Search Term'] == name]
            term1 = (b-a)
            term2 = (tempRaw - minR)/(maxR - minR)
            self.twitterDF['nImpactScore'][self.twitterDF['Search Term'] == name] = (term1*term2) + (a)
        self.twitterDF = self.twitterDF.drop(['Tweet ID', 'cVerified'],axis=1)
        return self.twitterDF
    
    def markovTweet(self,modelIn,tweetAbout):
        '''
        Takes two inputs, the now standard Twitter Data Frame and the
        list of trends to tweet about.
        Creates a markovify model out of each tweet for a particular keyword
        and returns a key dictionary pair that is relevant.
        Includes a hashtag with it
        '''
        self.modelIn = modelIn
        self.tweetAbout = tweetAbout
        self.model = [None] * len(self.tweetAbout)
        self.composed = dict()
        for i in range(len(self.tweetAbout)):
            self.modelInput = self.modelIn[self.modelIn['Search Term'] == self.tweetAbout[i]]['Tweet Text']
            #Converting to a string object to handle dependencies
            self.modelInput = self.modelInput.to_string(header = False, index = False)
            self.model[i] = markovify.Text(self.modelInput)
            #Handling Hashtags in the tweetAbout
            if self.tweetAbout[i][0] == '#':
                self.composed[self.tweetAbout[i]] = self.model[i].make_short_sentence(140) + self.tweetAbout[i]
            else:
                self.composed[self.tweetAbout[i]] = self.model[i].make_short_sentence(140) + ' #' + self.tweetAbout[i]
        return self.composed
'''HELPER FUNCTIONS'''
#Defining Tweet Scraper as a separate function outside the scope of the class
def tweetScraper(bot,trendsList,forTime=15,onceEvery=60,filename = (datetime.datetime.now().strftime('%m_%d_%Y') + ' tweetDump.csv'),save='N'):
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
    #Once again dropping duplicates to have a clean dataFrame
    tListAll = tListAll.drop_duplicates(subset='Tweet ID')   
    tListAll = tListAll.drop_duplicates(subset='Tweet Text')
    if save == 'Y':
        with open(filename,'a',encoding="UTF8") as file:
            tListAll.to_csv(file,header=True)
        print('Finished Scraping')
    return tListAll

def getLocation(locString):
    """
    Method to get the name or location of the closest match
    and return the weoid from the json
    """
    with open("weoidJSON.json", "r") as read_file:
        data = json.load(read_file)
    for i in data:
        if i['name'] == locString:
            return i['woeid']
        
#def plotTheBot(inputDF):
    
class predictImpact(object):
    def __init__(self,trainData,predictData):
        """
        features - List of features that the model is to be trained on
        Precondtion for the ML model is that the keywords should be the same
        as the ones in the Training model.
        """
        #Data Pre-processing
        self.trainData = trainData
        self.predictData = predictData
        self.predictData = self.predictData.drop(['Tweet ID','Created At','Tweet Text','Followers Count','User Handle','Sentiment Polarity'],axis = 1)
        self.predictData['nImpactScore'] = ""
        self.features =['Search Term','Retweeted','Retweet Count','Favorite Count']
    
    def encodeModel(self,inData):
        """
        Using One Shot Encoding to convert categorical variables into binary vectors
        """
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
        self.predictData['nImpactScore'] = self.val_predictions
        return self.predictData


if __name__ == '__main__':

    '''
    consumer_key = '<Your Consumer Key>'; 
    consumer_secret = '<Your Consumer Secret>'; 
    access_token = '<Your Access token>'; 
    access_token_secret = '<Your Access Token Secret>';
    '''
    consumer_key = 'x45FNED54ZkOzcWpK5I7KNkmT'; 
    consumer_secret = '9N4ABRaa9m6F2efgqlO1VP6014yoFcR1y29V51PuSMrOpwPpsX'; 
    access_token = '1057119039569489922-ltle8eR6UMBaYM0xwOYJ9GHPNU7PDF'; 
    access_token_secret = 'WIGeuVyguIYwjeA5lXJJWPUePK8KTIxEKuM5jPFT3DBcs';
    
    #Auth is a tweepy object to initialize a twitter bot.
    #Did not use in a function since the keys are private and it would be a wrapper around a wrapper.
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth)
    #Bot Initialization
    bot1 = NoobBot(api)
    #List of Trends to search for. Using New York as a placeholder but
    #this can be any location in the JSON file.
    trendsList = bot1.locTrends(getLocation('New York'))
    #Tweet Scrapping
    #Tweets can either be scraped on read in from a previously scrapped file
    #with the same column format.
    #scrappedTweets = tweetScraper(bot1,trendsList,forTime = 3,save='Y')
    scrappedTweets = pd.read_csv("12_06_2018 tweetDump.csv")
    #Calculating Impact Scores
    tweetImpact = bot1.calculateScore(scrappedTweets)
    #Defining a new set of data to predict for
    predictData = tweetScraper(bot1,trendsList,forTime=1)
    #Machine Learning Object, model defenition, prediction and assignment.
    mlObject = predictImpact(scrappedTweets,predictData)
    mlObject.buildModel()
    newP = mlObject.modelPredict()    
    #Compose tweets from the given list of trends.
    #tweetAbout = list(set(list(scrappedTweets['Search Term'])))
    composedTweets = bot1.markovTweet(scrappedTweets,trendsList)
