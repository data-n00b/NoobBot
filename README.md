# NoobBot
A twitter bot to record text sentiment using the TextBlob and Tweepy packages.
### Features to implement/update
* Better way to clean text, retain content while stripping 'RT', '@mentions', special characters and links.
* Track how many @mentions are there in the tweet (Optional)
* **DONE** Taken 0 polarity out of the picture.
  Formula for impact score and how to deal with 0 polarity if that is also taken into account. A linear equation with weighted co-      efficeitns might work.
* How we're handling updated tweets. ex. The evolution of likes and retweets on a tweet x hours from when it was first recorded. Either update numbers or ignore.
* **DONE** Update: Not considering predicting based on content. Just predicting based on keyword, retweets and favourites only. Original: For predicting, make sure we pick tweets that are newer than the newest tweet in the recorded set.
* **DONE** Machine learning model to predict impact score.
* Plottting (what details to plot if it is just impact over time or to include other factors also.
* GUI (optional)
* Markov tweet.
* Explore the `''.join` option for the cleanTweet method.
* `weoid` file added. Learn JSON parsing to directly fetch ids
