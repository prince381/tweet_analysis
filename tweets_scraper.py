import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
from textblob import TextBlob
from time import sleep
import json
import re
from stopwords import final_stopwords



# this function uses requests and BeautifulSoup to scrape the html of the twitter
# web page and extract all the html tags that contain the tweet informations and 
# put them all in a list.
def twitter_page_html(account_name):
    # This function is to handle twitter's dynamic page content loading using selenium
    site = 'https://twitter.com/{}'.format(account_name[1:])
    # get the first page
    page1 = requests.get(site)

    # parser the html page using BeautifulSoup
    soup = bs(page1.text,'html.parser')

    # find all the html tags that contains the tweet information
    lis_html = soup.find_all(name='li',attrs={'data-item-type':'tweet'})

    # get the next pointer 
    next_pointer = str(soup.find("div", {"class": "stream-container"})["data-min-position"])

    # perform loop to get the rest of the tweets
    for i in range(5):
        # get the next url
        next_url = 'https://twitter.com/i/profiles/show/{}/timeline/tweets?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false'.format(account_name[1:],next_pointer)
        try:
            next_response = requests.get(next_url)
        except Exception:
            return lis_html
        tweet_data = next_response.text
        tweets_obj = json.loads(tweet_data)
        if not tweets_obj["has_more_items"] and not tweets_obj["min_position"]:
            # using two checks here bcz in one case has_more_items was false but there were more items
            break
        next_pointer = tweets_obj["min_position"]
        html = tweets_obj["items_html"]
        new_soup = bs(html,'html.parser')
        new_list = new_soup.find_all(name='li',attrs={'data-item-type':'tweet'})
        # add the new tweet tags to the previous one
        lis_html += new_list
        
    return lis_html




# this function filters a given text and removes the stopwords as well as the links and tags from the text.
def remove_stopwords(text,stopwords=final_stopwords):
    tlist = TextBlob(text.lower())
    tlist = list(tlist.words)
    symbs = ['@','#','https','http','www.','.com','=',',',"'",'the','and','\'s']
    for i in symbs:
        for j in tlist:
            if i in j:
                tlist.remove(j)
            else:
                continue
    for wd in tlist:
        if wd in stopwords:
            tlist.remove(wd)
        else:
            continue
    return ' '.join(tlist)



# this function takes a text as an argument and translates it if it's not already in english
# after that calculate the sentiment score of the text and classifies it as negative,neutral or positive
def sentiment_score(text):
    #remove all stopwordsmlinks and tags from the tweet
    text = remove_stopwords(text,final_stopwords)
    # create a TextBlob object
    blob = TextBlob(text)
    # try and translate the text if it's not already in english
    try:
        new_blob = blob.translate(to='en')
    except Exception:
        new_blob = blob

    # calculate the sentiment
    sentiment = np.round(new_blob.sentiment.polarity,1)
    # classify the sentiment of the text
    if sentiment == 0:
        sentiment_type = 'neutral'
    elif sentiment < 0:
        sentiment_type = 'negative'
    else:
        sentiment_type = 'positive'

    # return the score and the sentiment type
    return sentiment,sentiment_type




# function to parse/handle the HTML and extract data using BeautifulSoup and pandas.DataFrame()
# and returns a data frame.
def scrape_data(html_list):
    # list for collecting tweet-texts
    texts = []
    # list for collecting tweet date
    date_time = []
    # list for collecting the sentiment score of each tweet
    sentimnt_score = []
    # list for collecting the sentiment type of each tweet
    sentimnt_type = []
    # list for collecting the number of replies
    replies = []
    # list for collecting the number of likes
    fav_counts = []
    # list for collecting the numbre of retweets
    retweets = []

    # loop through all the tweet tags and extract the neccessary information 
    for item in html_list:
        try:
            # get the text from each tweet
            text_container = item.find(name='div',attrs={'class':'js-tweet-text-container'})
            text = text_container.find('p').text
            #remove all stopwordsmlinks and tags from the tweet
            text = remove_stopwords(text,final_stopwords)
            # append the results in the texts list
            texts.append(text)
            # get the sentiment score and type for each tweet
            sentmt,smttp = sentiment_score(text)
            sentimnt_score.append(sentmt)
            sentimnt_type.append(smttp)

            # get the date and time the tweet was made and parse it using the dateutil.parser
            time_str = str(item.find(name='small',attrs={'class':'time'}).find('a'))
            time_list = time_str.split(' ')[7:13]
            time = time_list[0][-4:-1] +' '+ time_list[1]
            day = time_list[3]
            month = time_list[4]
            year = time_list[-1][0:4]
            fulldate = '{} {} {} {}'.format(day,month,year,time)
            # append the results in the date_time list
            date_time.append(fulldate)

            # the total number of replies of the tweet
            reply_container = item.find(name='button',attrs={'data-modal':'ProfileTweet-reply'})
            reply2 = reply_container.find(name='span',attrs={'class':'ProfileTweet-actionCount'})
            reply = reply2.find('span').text
            # append the results in the list of replies
            if reply == '':
                reply = 0
            else:
                reply = reply.replace('.','')
                reply = reply.replace('K','000')
                reply = int(reply)

            # get the total number of retweets
            retweet_container = item.find(name='button',attrs={'data-modal':'ProfileTweet-retweet'})
            retweet2 = retweet_container.find(name='span',attrs={'class':'ProfileTweet-actionCount'})
            retweet = retweet2.find('span').text
            # append the results in the list of retweets
            if retweet == '':
                retweet = 0
            else:
                retweet = retweet.replace('.','')
                retweet = retweet.replace('K','000')
                retweet = int(retweet)

            # get the total number of likes of a tweet
            likes_container = item.find(name='button',
                                        attrs={'class':'ProfileTweet-actionButton js-actionButton js-actionFavorite'})
            likes2 = likes_container.find(name='span',attrs={'class':'ProfileTweet-actionCount'})
            likes = likes2.find('span').text
            # append the results in the fav_counts list
            if likes == '':
                likes = 0
            else:
                likes = likes.replace('.','')
                likes = likes.replace('K','000')
                likes = int(likes)
            # check if values were picked by the html queries
            total_val = likes + reply + retweet
            # if not, perform another html query using different tags and classes
            if total_val == 0:
                action_tag = item.find(name='div',
                                      attrs={'class':'ProfileTweet-actionCountList u-hiddenVisually'})
                rep_container = action_tag.find(name='span',
                                               attrs={'class':'ProfileTweet-action--reply u-hiddenVisually'})
                rep2 = rep_container.find(name='span',
                                         attrs={'class':'ProfileTweet-actionCount'})['data-tweet-stat-count']
                retw_container = action_tag.find(name='span',
                                               attrs={'class':'ProfileTweet-action--retweet u-hiddenVisually'})
                retw2 = retw_container.find(name='span',
                                         attrs={'class':'ProfileTweet-actionCount'})['data-tweet-stat-count']
                fav_container = action_tag.find(name='span',
                                               attrs={'class':'ProfileTweet-action--favorite u-hiddenVisually'})
                fav2 = fav_container.find(name='span',
                                         attrs={'class':'ProfileTweet-actionCount'})['data-tweet-stat-count']
                reply = int(rep2)
                retweet = int(retw2)
                likes = int(fav2)
            retweets.append(retweet)
            fav_counts.append(likes)
            replies.append(reply)
        except Exception:
            continue
    # we now put the whole information in a data frame
    tweet_df = pd.DataFrame({'date':date_time,'tweet':texts,'sentiment_score':sentimnt_score,
                            'sentiment':sentimnt_type,'retweets':retweets,
                            'replies':replies,'likes':fav_counts})
    tweet_df.date = pd.to_datetime(tweet_df.date)

    return tweet_df



########################################################################################
#                                                                                      #
#   The two functions below were not put to use in this project but I thought it would #
#    be helpful to create them.One is being used inside the other and together,they    #
#    return the hastags used in a tweet and the number of times it appeared in the     #
#    tweets.                                                                           #
########################################################################################

# this function extracts all the hashtags from a tweet and store the into a list
def get_tags(df):
    # regular expression object for extracting the tags
    tag_regex = re.compile(r'#\w+')
    # loop over each tweet and get the hashtags
    tweets = df['tweet'].values
    all_tags = []
    for i in tweets:
        tags = tag_regex.findall(i)
        tags = [i.replace('pic','') for i in tags]
        tags = [i.lower() for i in tags]
        all_tags += tags

    # return a list of all hashtags
    return all_tags


# this function returns a series of hashtags and the number of times each appears
def tags_data(df):
    # get the list of all tags
    tags_list = get_tags(df)
    # create an empty dictionary for the tags
    tag_count = {}
    # loop over every hashtag in the list of tags and count the number of times each appears
    for tag in tags_list:
        tag_count.setdefault(tag,0)
        tag_count[tag] += 1

    # create the series of the hashtags
    series = pd.Series(tag_count)
    # sort in descending order
    sorted_series = series.sort_values(ascending=False)

    # return the series created
    return sorted_series

