import snscrape.modules.twitter as sntwitter
import pandas as pd
import time
from datetime import datetime, timedelta
import yfinance as yf
import praw
from pmaw import PushshiftAPI
import requests


def date_range(start: str, end: str):
    '''
    This function set the range of dates to fetch data. This functions returns a lit of dates in the given date range
    
    Inputs:
    start: Start date of date range
    end: End date of date range
    
    Output:
    List of dates in the given range
    '''
    start = pd.to_datetime(start, format = '%Y-%m-%d')
    end = pd.to_datetime(end, format = '%Y-%m-%d')
    delta = end - start  # as timedelta
    days = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
    return days


def get_twitter_data(keyword: str , start_date_list: list, end_date_list: list, data_path: str, per_day=100):
    '''
    This function return a csv file and dataframe of all required twitter data for a keyword in the given date range.
    
    Inputs:
    keyword: Word for which we have to fetch twitter data
    start_date_list: List of starting dates 
    end_date_list: List of ending dates
    data_path: Path to store data
    per_day: Maximum number tweets required per day
    
    Output:
    Dataframe and CSV file of twitter data. 
    
    '''
    tweets_list = []
    tweet_df = pd.DataFrame()
    start_time = time.time()
    iteration_time = time.time()
    # Using TwitterSearchScraper to scrape data and append tweets to list
    for date_index in range(len(start_date_list)):
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(str(company_name)+' since:' + str(start_date_list[date_index])+' until:'+str(end_date_list[date_index])+' lang:en').get_items()):
            tweets_list.append([tweet.content, tweet.user.username, tweet.date, tweet.id])
            tweet_df_temp = pd.DataFrame(tweets_list, columns=['text', 'user', 'date', 'Tweet Id'])
            tweet_df_temp.to_csv(data_path + company_name + '_twitter_data.csv')
            if i>per_day:
                break; 
        iteration_time_temp = time.time()
        print('Time Elapsed = ' + str(iteration_time_temp - iteration_time))
        iteration_time = iteration_time_temp
        print('Tweet for '+str(start_date_list[date_index])+' collected')
    return tweet_df    
        
def get_reddit_data(keyword: str , start_date_list: list, end_date_list: list, data_path: str, per_day=100):
    '''
    This function return a csv file and dataframe of all required reddit data for a keyword in the given date range.
    
    Inputs:
    keyword: Word for which we have to fetch reddit data
    start_date_list: List of starting dates 
    end_date_list: List of ending dates
    data_path: Path to store data
    per_day: Maximum number reddit comments required per day
    
    Output:
    Dataframe and CSV file of reddit data.
    
    '''
    
    comments_df = pd.DataFrame()
    api = PushshiftAPI()    

    for i in range(len(start_date_list)):
        after = int(datetime.strptime(start_date_list[i], "%Y-%m-%d").timestamp())
        before = int(datetime.strptime(end_date_list[i], "%Y-%m-%d").timestamp())
        limit=per_day
        comments = api.search_comments(q=company_name, limit=limit, before=before, after=after)
        comments_df_temp = pd.DataFrame(comments)
        comments_df_temp = comments_df_temp[['body', 'created_utc']]
        comments_df = comments_df.append(comments_df_temp)
    
    comments_df['date'] = comments_df['created_utc'].apply(lambda x: int(x))
    comments_df['date'] = comments_df['date'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'))
    comments_df.to_csv(company_name + '_reddit_data.csv')
    return comments_df


def get_finance_data(company_name: str, company_ticker: str, data_path: str):
    '''
    This function return a csv file and dataframe of all required finance data for a company name and ticker.
    
    Inputs:
    company_name: Company name for which we have to fetch finance data.
    company_ticker: Company ticker to fetch yahoo finance data.
    data_path: Path to store data
    
    Output:
    Dataframe and CSV file of finance data.
    
    '''
    finance_df = yf.download(company_ticker)
    finance_df.to_csv(data_path + company_name +'_finance_data.csv')
    return finance_df