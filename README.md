# Sentiment Analysis and Exploratory Data Analysis on tweets.

This is a machine learning project which focuses on performing sentiment and descriptive statistical analysis on twitter tweet data 
scraped from the twitter web page using python and textblob. This project is in two parts: 1. web scraping with requests and BeautifulSoup 
(these are tools are used for scraping data from the web in python) which will be done in a separated python script. 2. sentiment and 
descriptive statistical analysis which will be displayed in an interactive reporting dashboard. The reason for the dashboard is to allow 
you to perform the analysis on  any twitter user account you specify, provided it is valid. The sentiment analysis will be done using 
python’s textblob module.


## Dashboard demo.

![](https://github.com/prince381/tweet_analysis/blob/master/twitter_dash.gif)


# Textblob and Sentiment Analysis.

Textblob provides an API that perform Natural Language Processing tasks like Parts-of-Speech tagging, Noun Phrase Extraction, Sentiment 
analysis, Classification, Language detection and translation, etc. Textblob is built upon natural language toolkit (nltk).

Sentiment analysis is an example of text classification which is one of the most important tasks in Natural Language Processing. Sentiment 
analysis means analyzing the sentiment of a given text or document and categorizing the text/document into a specific class or category 
(like positive, neutral, and negative). In other words, we can say that sentiment analysis classifies any particular document as positive, 
negative or neutral. 

# Web Scraping

“ To those who have not developed the skill, computer programming can seem like a kind of magic. If programming is magic, then web 
scraping is wizardry; that is, the application of magic for particularly impressive and useful — yet surprisingly effortless — feats. “    
                    Ryan Mitchell – Collecting data from the modern web
                    

## What is Web Scraping ?

In theory, web scraping is the practice of gathering data through any means other than a program interacting with an API (or, obviously, 
through a human using a web browser). This is most commonly accomplished by writing an automated program that queries a web server, 
requests data (usually in the form of the HTML and other files that comprise web pages), and then parses that data to extract needed 
information. In practice, web scraping encompasses a wide variety of programming techniques and technologies, such as data analysis and 
information security.

## Why Web Scraping ?

Although browsers are handy for executing JavaScript, displaying images, and arranging objects in a more human-readable format (among 
other things), web scrapers are excellent at gathering and processing large amounts of data (among other things). Rather than viewing 
one page at a time through the narrow window of a monitor, you can view databases spanning thousands or even millions of pages at once.

Cited from: Ryan Mitchell – Collecting data from the modern web, O’Rielly Publication
