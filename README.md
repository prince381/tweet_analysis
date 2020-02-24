# Sentiment Analysis and Exploratory Data Analysis on tweets.

This is a machine learning project which focuses on performing sentiment and descriptive statistical analysis on twitter tweet data 
scraped from the twitter web page using python and textblob. This project is in two parts: 1. web scraping with requests and BeautifulSoup 
(these are tools are used for scraping data from the web in python) which will be done in a separated python script. 2. sentiment and 
descriptive statistical analysis which will be displayed in an interactive reporting dashboard. The reason for the dashboard is to allow 
you to perform the analysis on  any twitter user account you specify, provided it is valid. The sentiment analysis will be done using 
python’s textblob module.


## Dashboard demo.

![](https://github.com/prince381/tweet_analysis/blob/master/twitter_dash.gif)
### Project by: Prince Owusu
[Email](powusu381@gmail.com) || [linkedIn](https://www.linkedin.com/in/prince-owusu-356914198?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B2NYoXqMHQKOMp0yWSME5mQ%3D%3D) || [@iam_kwekhu](https://twitter.com/iam_kwekhu)

# Run the app locally on your PC.

To get the app to run on your local computer,I suggest you install git and create a separate virtual environment running python3 for this app and install all of the required dependencies there.Run in the terminal/command prompt.

install git on linux

> $ sudo apt-get update

...

> $ sudo apt-get install git


or dowmload the latest version of [Git for Windows installer](https://gitforwindows.org) and [Git for Mac OS installer](https://sourceforge.net/projects/git-osx-installer/files/)

configure your Git username and email using the following commands:

> git config --global user.name "YOUR USERNAME"

...

> git config --global user.email "YOUR EMAIL"

clone this project repository and create a separate virtual environment:

> git clone https://github.com/prince381/tweet_analysis.git

...

> cd tweet_analysis

...

> python3 -m virtualenv venv


In UNIX systems:

> source venv/bin/activate

In windows:

> venv\Scripts\activate


To install all of the required packages to this environment,simply run

> pip install -r requirements.txt

and all the required pip packages,will be installed,and the app will be able to run.

Run this app locally by:

> python app.py


Open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in your browser.
