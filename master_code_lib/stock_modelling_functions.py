#Importing Libraries
import numpy as np
import pandas as pd

def regression_data_preprocessing(df, sentiment=True):
    '''
    This function is used to select the required features from the processed input dataframe for the regression model input.
    
    Inputs:
    df: Processed Dataframe of Sentiment score and Financial data.
    sentiment: Boolen input, True if we want to include sentiment features in input to model and False if we dont want to include sentiment features in input to regression model.
    
    Output:
    Dataframe that can be used as input to regression model. 
    
    '''
    df = df.dropna()
    if sentiment==True:
        df = df[["Open","High","Low","Close", "Adj Close", "Volume", "ts_polarity", "twitter_volume"]]
    if sentiment==False:
        df = df[["Open","High","Low","Close", "Adj Close", "Volume", "twitter_volume"]]
    df["Pct_change"] = df["Adj Close"].pct_change()
    # Drop null values
    df = df.dropna()
    
    return df 

def classifier_data_preprocessing(df, sentiment=True):
    '''
    This function is used to select the required features from the processed input dataframe for the classifier model input.
    
    Inputs:
    df: Processed Dataframe of Sentiment score and Financial data.
    sentiment: Boolen input, True if we want to include sentiment features in input to model and False if we dont want to include sentiment features in input to classifier model.
    
    Output:
    X: Dataframe of required features
    y: Target Vector array
    
    '''
    
    df = df.dropna()
    df = df.set_index("Date")
    sentiment = [] 
    for score in df['ts_polarity']:
        if score >= 0.05 :
            sentiment.append("Positive") 
        elif score <= - 0.05 : 
            sentiment.append("Negative")        
        else : 
            sentiment.append("Neutral")   

    df["Sentiment"] = sentiment
    #Stock Trend based on difference between current price to previous day price and coverting them to '0' as fall and '1' as rise in stock price
    df['Price Diff'] = df['Adj Close'].diff()
    df = df.dropna()
    df['Trend'] = np.where(df['Price Diff'] > 0 , 1, 0)
   
    if sentiment==False:
        df_final = df[["Open","High","Low","Close","Adj Close", "Volume","Trend"]]    
    
    else:
        
        df_final = df[["Open","High","Low","Close","Adj Close", "Volume", 'twitter_volume', "Sentiment", "Trend"]]
        df_final = pd.get_dummies(df_final, columns=["Sentiment"])
        
    X = df_final.copy()
    X = X.drop("Trend", axis=1)
    y = df_final["Trend"].values.reshape(-1, 1)
    
    return X,y


def data_train_test_split(X, y, split):
    '''
    This function is used to split the X and y data intomtrain and test sets
    
    Inputs:
    X: Dataframe of Features
    y: Array of Target labels
    split: Percentage of dataset in training set
    
    Output:
    X_train, X_test, y_train, y_test
    
    '''
    X_split = int(split * len(X))
    y_split = int(split * len(y))

    # Set X_train, X_test, y_train, t_test
    X_train = X[: X_split]
    X_test = X[X_split:]
    y_train = y[: y_split]
    y_test = y[y_split:]
    
    return X_train, X_test, y_train, y_test
    
def window_data(df, window, feature_col_number1, feature_col_number2, feature_col_number3, target_col_number):
    '''
    The first step towards preparing the data was to create the input features `X` and the target vector `y`. 
    We used the `window_data()` function to create these vectors.
    This function chunks the data up with a rolling window of _X_t - window_ to predict _X_t_.
    The function returns two `numpy` arrays:
    
    Inputs:

    df: The original DataFrame with the time series data.
    window: The window size in days of previous closing prices that will be used for the prediction.
    feature_col_number: The column number from the original DataFrame where the features are located.
    target_col_number: The column number from the original DataFrame where the target is located.
    
    
    Outputs:
    
    X: The input features vectors.
    y: The target vector.
    
    '''
    
    # Create empty lists "X_close", "X_polarity", "X_volume" and y
    X_close = []
    X_polarity = []
    X_volume = []
    y = []
    for i in range(len(df) - window):
        
        # Get close, ts_polarity, twitter_vol, and target in the loop
        close = df.iloc[i:(i + window), feature_col_number1]
        ts_polarity = df.iloc[i:(i + window), feature_col_number2]
        tw_vol = df.iloc[i:(i + window), feature_col_number3]
        target = df.iloc[(i + window), target_col_number]
        
        # Append values in the lists
        X_close.append(close)
        X_polarity.append(ts_polarity)
        X_volume.append(tw_vol)
        y.append(target)
        
    return np.hstack((X_close,X_polarity,X_volume)), np.array(y).reshape(-1, 1)

