import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import dash_daq as daq
from flask_caching import Cache
import plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from tweets_scraper import twitter_page_html,scrape_data
from textblob import TextBlob



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
                                   'margin-left':'5px',
                                   'margin-right':'5px'})],
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
                                   'margin-left':'5px',
                                   'margin-right':'5px'})],
                     style={'backgroundColor':'skyblue',
                           'border-radius':20,
                           'border-top':'1px solid lightgrey',
                           'border-left':'1px solid lightgrey',
                           'border-right':'4px solid lightgrey',
                           'border-bottom':'4px solid lightgrey',
                           'textAlign':'center'})
            
        ],className='three columns'),
        
        html.Div(children=[
            
            html.P([html.A(['gmail: powusu381@gmail.com'],
                              href='powusu381@gmail.com',
                             style={'color':'white',
                                   'margin-left':'5px',
                                   'margin-right':'5px'})],
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
                           href='https://github.com/prince381',
                           style={'color':'white',
                                   'margin-left':'5px',
                                   'margin-right':'5px'})],
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
