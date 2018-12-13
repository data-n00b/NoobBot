# NoobBot
### Overview
Aggregate twitter data based on keywords and location input. Measure impact of tweets over time based on user status and tweet engagement metrics. Predict impact of these keywords over time. Procedurally generate relatively original content from the data that has been gathered for each keyword.

### Dependencies
* Requires the `tweepy` , `markovify` and `textblob` packages.
* Requires the `weoidJSON.json` file as part of the source code to meet location input details.
* A developer twitter account to authenticate with tweepy. [I referred to this link to create a Twitter App and authenticate it on Python](https://www.digitalocean.com/community/tutorials/how-to-create-a-twitter-app)

### Method defenitions and Basic Usage
* Once authenticated, create an object of the `NoobBot` class with the authenticated API object. The `NoobBot` object will be used to access the major features of the application.
* `locTrends` returns the list of trends for a particular location. Takes two inputs and they are loaded as defaults. `getLocation` is a helper function that takes a location string input and returns the [*woeid*](https://en.wikipedia.org/wiki/WOEID) (Where on Earth ID) from the JSON file.
* `__searchTweets` takes an search query and returns a pandas dataframe with the following information about the Tweet, **Search Term, Tweet ID, Created At, Tweet Text, Retweeted(Boolean), Retweet Count, Favorite Count, Followers Count, Is Verified(Boolean), User Handle and Sentiment Polarity**.
* `cleanTweet` is an internal method to strip the tweet of *@mentions, links, trailing and leading whitespaces and braces*. 
* `tweetSentiment` is also an internal method that relies on the [**TextBlob**](https://textblob.readthedocs.io/en/dev/index.html) package to assign an sentiment score to each tweet.
* `calculateScore` considers the factors in each tweet and returns a value between -1 and 1 that captures the impact of a tweet on the twitterverse. Can be modified to fit a custom value.
* `markovTweet` (no relation to Markov Chains) is an extension on the [**markovify**](https://github.com/jsvine/markovify) package to procedurally generate tweets based on scaped data from the bot.
* `tweetScrapper` is a helper function that takes a list of keywords and continually scrapes twitter once a minute for a user defined amount of time with the option to save the dataframe as a CSV file. Recommended to use this instead of directly using the `__searchTweets` method.
* `plotTheBot` is a basic plotting function to visualize the impact score of each keyword over time to identify trends and see where each score lies.
* `predictImpact` is a class with a basic DecisionTreeRegressor model from the `scikit-learn` package.
* Refer to the main function in the source code for an simple example of the essential functions.
