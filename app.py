import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from flask_caching import Cache
import plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import json
#from tweets_scraper import twitter_page_html,scrape_data
from textblob import TextBlob



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


stopwords = '''
a
able
about
above
according
accordingly
across
actually
after
afterwards
again
against
ain't
all
allow
allows
almost
alone
along
already
also
although
always
am
among
amongst
an
and
another
any
anybody
anyhow
anyone
anything
anyway
anyways
anywhere
apart
appear
appreciate
appropriate
are
aren't
around
as
a's
aside
ask
asking
associated
at
available
away
awfully
be
became
because
become
becomes
becoming
been
before
beforehand
behind
being
believe
below
beside
besides
best
better
between
beyond
both
brief
but
by
came
can
cannot
cant
can't
cause
causes
certain
certainly
changes
clearly
c'mon
co
com
come
comes
concerning
consequently
consider
considering
contain
containing
contains
corresponding
could
couldn't
course
c's
currently
definitely
described
despite
did
didn't
different
do
does
doesn't
doing
don
done
don't
down
downwards
during
each
edu
eg
eight
either
else
elsewhere
enough
entirely
especially
et
etc
even
ever
every
everybody
everyone
everything
everywhere
ex
exactly
example
except
far
few
fifth
first
five
followed
following
follows
for
former
formerly
forth
four
from
further
furthermore
get
gets
getting
given
gives
go
goes
going
gone
got
gotten
greetings
had
hadn't
happens
hardly
has
hasn't
have
haven't
having
he
he'd
he'll
hello
help
hence
her
here
hereafter
hereby
herein
here's
hereupon
hers
herself
he's
hi
him
himself
his
hither
hopefully
how
howbeit
however
how's
i
i'd
ie
if
ignored
i'll
i'm
immediate
in
inasmuch
inc
indeed
indicate
indicated
indicates
inner
insofar
instead
into
inward
is
isn't
it
it'd
it'll
its
it's
itself
i've
just
keep
keeps
kept
know
known
knows
last
lately
later
latter
latterly
least
less
lest
let
let's
like
liked
likely
little
look
looking
looks
ltd
mainly
many
may
maybe
me
mean
meanwhile
merely
might
more
moreover
most
mostly
much
must
mustn't
my
myself
name
namely
nd
near
nearly
necessary
need
needs
neither
never
nevertheless
new
next
nine
no
nobody
non
none
noone
nor
normally
not
nothing
novel
now
nowhere
obviously
of
off
often
oh
ok
okay
old
on
once
one
ones
only
onto
or
other
others
otherwise
ought
our
ours
ourselves
out
outside
over
overall
own
particular
particularly
per
perhaps
placed
please
plus
possible
presumably
probably
provides
que
quite
qv
rather
rd
re
really
reasonably
regarding
regardless
regards
relatively
respectively
right
s
said
same
saw
say
saying
says
second
secondly
see
seeing
seem
seemed
seeming
seems
seen
self
selves
sensible
sent
serious
seriously
seven
several
shall
shan't
she
she'd
she'll
she's
should
shouldn't
since
six
so
some
somebody
somehow
someone
something
sometime
sometimes
somewhat
somewhere
soon
sorry
specified
specify
specifying
still
sub
such
sup
sure
t
take
taken
tell
tends
th
than
thank
thanks
thanx
that
thats
that's
the
their
theirs
them
themselves
then
thence
there
thereafter
thereby
therefore
therein
theres
there's
thereupon
these
they
they'd
they'll
they're
they've
think
third
this
thorough
thoroughly
those
though
three
through
throughout
thru
thus
to
together
too
took
toward
towards
tried
tries
truly
try
trying
t's
twice
two
un
under
unfortunately
unless
unlikely
until
unto
up
upon
us
use
used
useful
uses
using
usually
value
various
very
via
viz
vs
want
wants
was
wasn't
way
we
we'd
welcome
well
we'll
went
were
we're
weren't
we've
what
whatever
what's
when
whence
whenever
when's
where
whereafter
whereas
whereby
wherein
where's
whereupon
wherever
whether
which
while
whither
who
whoever
whole
whom
who's
whose
why
why's
will
willing
wish
with
within
without
wonder
won't
would
wouldn't
yes
yet
you
you'd
you'll
your
you're
yours
yourself
yourselves
you've
zero'''

final_stopwords = stopwords.split('\n')



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


external = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__,external_stylesheets=external)

server = app.server

app.title = 'Tweet Analyzer'

cache = Cache(server,config={'CACHE_TYPE':'simple'})
timeout = 120


@cache.memoize(timeout=timeout)
def get_dataframe(username):
    try:
        html_list = twitter_page_html(username)
        data = scrape_data(html_list)
        return data
    except Exception:
        return ''


def word_count(data):
    wrds = []
    for text in data.tweet.values:
        blob = TextBlob(text)
        try:
            newblob = blob.translate(to='en')
        except Exception:
            newblob = blob
        wrdlist = newblob.words
        wrds += wrdlist
    wrd_count = {}
    for i in wrds:
        if (len(i) >= 3) and (('https' or 'http') not in i) and ('www.' not in i) and ('.com' not in i) and ('#' not in i):
            wrd_count.setdefault(i.lower(),0)
            wrd_count[i.lower()] += 1
        else:
            continue
    df = pd.Series(wrd_count)
    df = df.sort_values(ascending=False)
    return df.head(15)

def render_chart(data,height=400):
    x = data.index
    y = data.values
    plot = [
        go.Bar(x=x,
              y=y,
              marker={'line':{'width':.2}},
              opacity=.8)
    ]

    layout = go.Layout(title='<b>15 frequently used words in recent tweets</b>',
                       height=height,
                      xaxis={'showgrid':False,
                            'title':'<b>words</b>',
                            'tickfont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },'titlefont':{
                                'size':15
                            }},
                      yaxis={'title':'<b>frequency</b>',
                            'tickfont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },'titlefont':{
                                'size':15
                            }})
    return plot,layout


def make_colors(vals):
    colors = []
    for i in vals:
        if i < 0:
            colors.append('red')
        elif i == 0:
            colors.append('skyblue')
        else:
            colors.append('purple')
    return colors

def sentiment_chart(df):
    newdf = df.set_index('date')
    x = newdf.index
    y = newdf.sentiment_score.values
    text = newdf.sentiment.values
    colors = make_colors(y)
    count = newdf.sentiment.value_counts()
    total = count.sum()
    count_lis = []
    for i in count.index:
        if i == 'positive':
            color = 'purple'
            position = 0
        elif i == 'neutral':
            color = 'skyblue'
            position = 0.4
        else:
            color = 'red'
            position = 0.8
        tup = (i,(count[i]/total)*100,color,position)
        count_lis.append(tup)
    annotations = []
    for i,j,k,l in count_lis:
        annotations.append({'x':l,'y':0.9,
                           'xref':'paper','yref':'paper',
                           'xanchor':'left','yanchor':'bottom',
                           'align':'left','showarrow':False,
                           'text':'<b>{} sentiments {}%</b>'.format(i,j),
                           'font':{'color':k}})
    plot = [
        go.Scatter(x=x,
                  y=y,
                  mode='markers',
                  marker={'size':6,'color':colors},
                  opacity=.6,
                  text=text)
    ]

    layout = go.Layout(title='<b>sentiment score for each tweet</b>',
                       xaxis={'showgrid':False,
                            'title':'<b>date of tweet</b>',
                            'tickfont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },'titlefont':{
                                'size':15
                            }},
                      yaxis={'title':'<b>sentiment score</b>',
                            'tickfont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },'titlefont':{
                                'size':15
                            }},
                      hovermode='closest',
                      height=315)
    return plot,layout


def sentiment_summary(df):
    sent_count = df['sentiment'].value_counts()
    pos_count = sent_count['positive']
    neu_count = sent_count['neutral']
    try:
        neg_count = sent_count['negative']
        return pos_count,neu_count,neg_count
    except Exception:
        neg_count = 0
        return pos_count,neu_count,neg_count

def tweet_statistics(df):
    avg_likes = df['likes'].median()
    avg_retweets = df['retweets'].median()
    avg_replies = df['replies'].median()
    return int(avg_likes),int(avg_retweets),int(avg_replies)



app.config.suppress_callback_exceptions = True
app.layout = html.Div(children=[
    
    html.Div(children=[
        
        html.Div(children=[
            
            html.P([html.Img(src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcAn3uFDwtG3shW27HIXMXjVwCLJjGk-v-b1ceIBLxjp3yynthAw&s',
                             height=30,width=40,
                            style={'margin-left':15,
                                  'margin-right':15})
                     ,'your recent tweets analysis dashboard'],style={'color':'white',
                                                                      'fontSize':30})
            
        ],className='seven columns'),

        html.Div(children=[
            
            dcc.Input(id='username',type='text',
                      placeholder='enter a valid username.eg.@richard',
                     value='',size=30),
            
            html.Button(id='get_tweet',children=['analyze'],
                       style={'margin-left':5,
                             'backgroundColor':'white'})
            
        ],className='five columns',style={'margin-top':10,
                                          'margin-bottom':5,
                                          'margin-left':15,
                                          'display':'inline-block'})
        
    ],className='row header',
            style={'backgroundColor':'#111111',
                  'border-top':'1px solid lightgrey',
                  'border-left':'1px solid lightgrey',
                  'border-right':'4px solid lightgrey',
                  'border-bottom':'4px solid lightgrey',
                  'border-radius':5}),
    
    dcc.Loading(id='loading1',children=[
      
        html.Div(id='output-component',
                 className='row',
                 style={'margin-top':20,
                      'margin-left':20,
                       'margin-right':20})
        
    ],type='circle'),
    
    html.Br(),
    
    html.Div(children=[
        
        html.Div(children=[
            
            html.P([html.A(['created by: Prince Owusu'],
                             style={'color':'white',
                                   'margin-left':12,
                                   'margin-right':12})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey',
                           'textAlign':'center'})
            
        ],className='three columns'),
        
        html.Div(children=[
            
            html.P([html.A(['twitter: @iam_kwekhu'],
                              href='https://twitter.com/iam_kwekhu',
                             style={'color':'white',
                                   'margin-left':12,
                                   'margin-right':12})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey',
                           'textAlign':'center'})
            
        ],className='three columns'),
        
        html.Div(children=[
            
            html.P([html.A(['powusu381@gmail.com'],
                              href='powusu381@gmail.com',
                             style={'color':'white',
                                   'margin-left':12,
                                   'margin-right':12})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey',
                           'textAlign':'center'})
            
        ],className='three columns'),
        
        html.Div(children=[
            
            html.P([html.A(['github: prince381'],
                           href='https://github.com/prince381/tweet_analysis',
                           style={'color':'white',
                                   'margin-left':12,
                                   'margin-right':12})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey',
                           'textAlign':'center'})
            
        ],className='three columns')
        
    ],className='row',
            style={'margin-left':20,
                  'margin-right':20})
    
])


@app.callback(Output('output-component','children'),
             [Input('get_tweet','n_clicks')],
             [State('username','value')])
@cache.memoize(timeout=timeout)
def return_output(n_clicks,username):
    not_found_page = [
                html.Center(children=[
                    html.H5('You have not entered a valid username or the system could not fetch the tweets for {}'.format(username),
                           style={'color':'skyblue'}),
                    html.Details(children=[
                        html.Summary('fetching and analysis of tweets could take 2 to 4 minutes to complete,so please be patient when the system is loading',
                                    style={'fontFamily':'Raleway',
                                          'color':'#111111'})
                    ]),
                    html.Br(),
                    html.Img(src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfj4jW-GfiW_B0zGK4ETHXu5cah84WYdpQ_ENuup1EM1qDOxgLQA&s',
                             height=400,width=500)
                ])
            ]
    
    data = get_dataframe(username)
    if type(data) == str:
        return not_found_page
    else:
        avglikes,avgretweets,avgreply = tweet_statistics(data)
        possent,neusent,negsent = sentiment_summary(data)
        word_data = word_count(data)
        word_plot = render_chart(word_data,height=460)[0]
        word_layout = render_chart(word_data,height=460)[1]
        output_content = [
            html.Div(children=[
                
                html.P([html.P('fetched and analyzed {} recent tweets for {}'.format(data.shape[0],username),
                             style={'fontSize':20,
                           'color':'white',
                           'margin-left':12,
                           'margin-right':12})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'width':'50%',
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey'})
                
            ],className='row'),
            
            html.Br(),
            
            html.Div(children=[
                
                html.Div(children=[
                    
                    html.Div(children=[
                        
                        html.Div(children=[
                    
                            html.P(children=[

                                html.P('average likes',style={'textAlign':'center'}),
                                html.P('{}'.format(avglikes),style={'color':'skyblue',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('per tweet',style={'textAlign':'center'})

                            ])
                    
                        ],style={'border-top':'1px solid lightgrey',
                               'border-left':'1px solid lightgrey',
                               'border-right':'4px solid lightgrey',
                               'border-bottom':'4px solid lightgrey',
                              'border-radius':5}),
                        
                        html.Br(),
                        html.Br(),

                        html.Div(children=[

                            html.P(children=[

                                html.P('average retweets',style={'textAlign':'center'}),
                                html.P('{}'.format(avgretweets),style={'color':'skyblue',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('per tweet',style={'textAlign':'center'})

                            ])

                        ],style={'border-top':'1px solid lightgrey',
                               'border-left':'1px solid lightgrey',
                               'border-right':'4px solid lightgrey',
                               'border-bottom':'4px solid lightgrey',
                              'border-radius':5}),
                        
                        html.Br(),
                        html.Br(),

                        html.Div(children=[

                            html.P(children=[

                                html.P('average replies',style={'textAlign':'center'}),
                                html.P('{}'.format(avgreply),style={'color':'skyblue',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('per tweet',style={'textAlign':'center'})

                            ])

                        ],style={'border-top':'1px solid lightgrey',
                               'border-left':'1px solid lightgrey',
                               'border-right':'4px solid lightgrey',
                               'border-bottom':'4px solid lightgrey',
                              'border-radius':5}),

                    ],className='three columns'),
                    
                    html.Div(children=[
                        
                        dcc.Graph(id='chart_1',
                                 figure={
                                     'data':word_plot,
                                     'layout':word_layout
                                 })
                        
                    ],className='nine columns',
                             style={'border-top':'1px solid lightgrey',
                                   'border-left':'1px solid lightgrey',
                                   'border-right':'4px solid lightgrey',
                                   'border-bottom':'4px solid lightgrey',
                                   'border-radius':5,
                                   'display':'inline-block'})
                    
                ],className='seven columns'),
                
                html.Div(children=[
                    
                    html.Div(children=[
                
                        html.Div(children=[
                            
                            html.P(children=[

                                html.P('positive sentiments',style={'textAlign':'center'}),
                                html.P('{}'.format(sentiment_summary(data)[0]),style={'color':'purple',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('tweets',style={'textAlign':'center'})

                            ])

                        ],className='four columns',
                                style={'border-top':'1px solid lightgrey',
                                       'border-left':'1px solid lightgrey',
                                       'border-right':'4px solid lightgrey',
                                       'border-bottom':'4px solid lightgrey',
                                      'border-radius':5}),

                        html.Div(children=[
                            
                            html.P(children=[

                                html.P('neutral sentiments',style={'textAlign':'center'}),
                                html.P('{}'.format(sentiment_summary(data)[1]),style={'color':'skyblue',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('tweets',style={'textAlign':'center'})

                            ])

                        ],className='four columns',
                                style={'border-top':'1px solid lightgrey',
                                       'border-left':'1px solid lightgrey',
                                       'border-right':'4px solid lightgrey',
                                       'border-bottom':'4px solid lightgrey',
                                      'border-radius':5}),

                        html.Div(children=[
                            
                            html.P(children=[

                                html.P('negative sentiments',style={'textAlign':'center'}),
                                html.P('{}'.format(sentiment_summary(data)[2]),style={'color':'red',
                                                                   'fontSize':30,
                                                                   'textAlign':'center'}),
                                html.P('tweets',style={'textAlign':'center'})

                            ])

                        ],className='four columns',
                                style={'border-top':'1px solid lightgrey',
                                       'border-left':'1px solid lightgrey',
                                       'border-right':'4px solid lightgrey',
                                       'border-bottom':'4px solid lightgrey',
                                      'border-radius':5})

                        ],className='row'),
                    
                    html.Br(),
                    
                    html.Div(children=[
                        
                        dcc.Graph(id='sentiment_chart',
                                 figure={
                                     'data':sentiment_chart(data)[0],
                                     'layout':sentiment_chart(data)[1]
                                 })
                        
                    ],className='row',
                            style={'border-top':'1px solid lightgrey',
                                   'border-left':'1px solid lightgrey',
                                   'border-right':'4px solid lightgrey',
                                   'border-bottom':'4px solid lightgrey',
                                  'border-radius':5})

                ],className='five columns')
                
            ],className='row')
        ]
        
        return output_content
    


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
if __name__ == '__main__':
    app.run_server(debug=False)
