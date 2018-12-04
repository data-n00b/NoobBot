# NoobBot
A twitter bot to record text sentiment using the TextBlob and Tweepy packages.

### What it does.
* Given a location, returns a list of topics trending in that location. Defaults to Worldwide.
* Monitors twitter activity to gather tweets for a custom interval. Defaults to gathering every minute for three minutes.
* Calculates an impact score for the tweet with factors inculding number of retweets, sentiment of the content and popularity of the user.
* A machine learning algorithm then predicts the evolution of the sentiment for the same keywords overtime, with only the number of retweets and user status without looking at the content of the tweet.

### Under Development
* Custom selection of user location based on string input (current input is WOEID number)
* Markov text generation to automatically tweet content with a new method.

### Features to implement/update
* Better way to clean text, retain content while stripping 'RT', '@mentions', special characters and links. *Couple core issues around cleaning the text, post which generated content will be normal.*
* Explore the `''.join` option for the cleanTweet method.
* Track how many @mentions are there in the tweet (Optional)
* **DONE** Taken 0 polarity out of the picture.
  Formula for impact score and how to deal with 0 polarity if that is also taken into account. A linear equation with weighted co-      efficeitns might work.
* How we're handling updated tweets. ex. The evolution of likes and retweets on a tweet x hours from when it was first recorded. Either update numbers or ignore. *Probably not handling this*
* **DONE** Update: Not considering predicting based on content. Just predicting based on keyword, retweets and favourites only. Original: For predicting, make sure we pick tweets that are newer than the newest tweet in the recorded set.
* **DONE** Machine learning model to predict impact score.
* Plottting (what details to plot if it is just impact over time or to include other factors also.
* GUI (optional)
* **DONE** Markov tweet.
* **DONE** `weoid` file added. Learn JSON parsing to directly fetch ids. Dependency is that the woeidJSON file should be located in the same folder in which the script is running.
