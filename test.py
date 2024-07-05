import sys
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import pandas as pd
import time
from colorama import Fore, Back, Style, init
from termcolor import colored, cprint
from datetime import date, timedelta, datetime
from yahooquery import Ticker
from pandas_datareader import data as wb
from nsetools import Nse
nse=Nse()
from nsepy import get_history
import stockstats
from stockstats import StockDataFrame
import twilio
from twilio.rest import Client
import stock_indicators as si
pd.set_option('display.max_rows',None)
pd.set_option('display.expand_frame_repr',None)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from INDICATOR import Stratergy_one, run

def aaa(x=0,y=0):
    if (x>0) & (y<0) | (x<0) & (y>0) | ((x>0) & (y>0) & (x<y)) | ((x<0) & (y<0) & (x<y)):
        result=y-x
    elif  ((x>0) & (y>0) & (x>y)) | ((x<0) & (y<0) & (x>y)):
        result=x-y
    else:
        result=0
    return(result)
    


#data=yf.download("CONCOR.NS",period='1d',interval='5m',progress=False)
#data=pd.DataFrame(data)
#data=data.reset_index()
#msg_rep=['On 2024-07-04 09:10:00+05:30 BUY WIPRO']
data=Stratergy_one('HAVELLS',48,3,20,50,100)
start_date=str(date.today()) #str(date.today()-timedelta(days=2))
for i, row in data.iterrows():
    data.loc[i,"dis"]=aaa(data.loc[i,"macds"],data.loc[i,"macdh"])
    data['dis']=abs(data.macds)-abs(data.macdh)
print(data[['Datetime','close','macd','macds','macdh','macd_buy_sell','BUY_SELL','dis']])
#print(aaa(-1,5),aaa(5,-1),aaa(5,1),aaa(1,5),aaa(-1,-5),aaa(-5,-1),aaa())
#run()
'''
x=data[['Open','High','Low','Volume']]
x.sort_index()
y=data[['Close']]
y.sort_index()
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=42)
model=LinearRegression()
model.fit(x_train,y_train)
pred=model.predict(x_test)

print(pred)
'''