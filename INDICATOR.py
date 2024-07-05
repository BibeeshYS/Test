# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 15:54:36 2020

@author: BibeeshYS
"""


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
def macd_alignment(x):
    if x<1000:
        y=6
    elif x<1500:
        y=8
    elif x<=2000:
        y=10
    else:
        y=11
    return y
    

def color_red_green(val):
    if val < 0:
        # color = Fore.RED
        color = Back.RED
    else:
        # color = Fore.GREEN
        color = Back.GREEN
    return color  + str('{0:0}'.format(val))+ Style.RESET_ALL
def color_text(val):
    if val == 'SELL':
        # color = Fore.RED
        color = Back.RED
    else:
        # color = Fore.GREEN
        color = Back.GREEN
    return color  + str('{0:0}'.format(val))+ Style.RESET_ALL
def clearline_1msg(msg):
    CURSOR_UP_ONE = '\033[K'
    ERASE_LINE = '\x1b[2K'
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE+"\r")
    print(msg, end='                                                 \r')
   


def clearline(msg,msg2):
    CURSOR_UP_ONE = '\033[K'
    ERASE_LINE = '\x1b[2K'
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE+'\r')
    print(msg,msg2, end='                                                 \r')


def countdown_timer_MTM(t,calling_function1,calling_function2):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        clearline(calling_function1(),timer)
        # print(Target_Base[["SYMBOL","TGT"]])        
        t -= 5
        time.sleep(5)
        # print("\033[H\033[J")    
    calling_function2()

def countdown(t,calling_function):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        clearline_1msg(timer)        
        t -= 1
        time.sleep(1)
        # print("\033[H\033[J")
    calling_function()

def twlio(msg,too):
    account_sid = 'ACcdbe3073da3cca3db9474335567928ee'
    auth_token  = "ae94facd386899c76d148d35635b834e"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=msg,
            to='whatsapp:'+too)
    #print(message.sid)

def Super_Trend_SMA_EMA_MACD_ADX_PIVOT(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA,Period,Interval):
    data =yf.download(Stock_name+".NS", period=Period,interval=Interval,progress=False)
    data.columns=["open","high","low","close","amount","volume"]
    data=StockDataFrame(data)
    data.get('boll')
    data.get('adx')
    data.get("macd")
    data=data.assign(sma_50=data["close"].rolling(50).mean())
    data=pd.DataFrame(data)
    data=data.reset_index()

    data=data.assign(BUB=0.00)
    data=data.assign(BLB=0.00)
    data=data.assign(FUB=0.00)
    data=data.assign(FLB=0.00)
    data=data.assign(ST=0.00)
    data=data.assign(ATR=data["tr"].rolling(Supertrend_period).mean())
    data=data.assign(ATR= data["ATR"].replace('nan', np.nan).fillna(0))                                      
    data=data.assign(BUB= round(((data["high"] + data["low"]) / 2) + (Supertrend_length * data["ATR"]),2))
    data=data.assign(BLB= round(((data["high"] + data["low"]) / 2) - (Supertrend_length * data["ATR"]),2))
    data=data.assign(FUB = data["FUB"].replace('nan', np.nan).fillna(0))

    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FUB"]=0.00
        else:
            if (data.loc[i,"BUB"]<data.loc[i-1,"FUB"])|(data.loc[i-1,"close"]>data.loc[i-1,"FUB"]):
                data.loc[i,"FUB"]=data.loc[i,"BUB"]
            else:
                data.loc[i,"FUB"]=data.loc[i-1,"FUB"]
    
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FLB"]=0.00
        else:
            if (data.loc[i,"BLB"]>data.loc[i-1,"FLB"])|(data.loc[i-1,"close"]<data.loc[i-1,"FLB"]):
                data.loc[i,"FLB"]=data.loc[i,"BLB"]
            else:
                data.loc[i,"FLB"]=data.loc[i-1,"FLB"]               
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"ST"]=0.00
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"]) & (data.loc[i,"close"]<=data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"])&(data.loc[i,"close"]>data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]>=data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]<data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]

    for i, row in data.iterrows():
       if i<=2:
           data.loc[i,"ema_5"]=0.00
           data.loc[i,"ema_20"]=0.00
       else:
           data.loc[i,"ema_5"]=data.loc[i,"close"]*(2/(EMA_1+1))+data.loc[i-1,"ema_5"]*(1-(2/(EMA_1+1)))
           data.loc[i,"ema_20"]=data.loc[i,"close"]*(2/(EMA_2+1))+data.loc[i-1,"ema_20"]*(1-(2/(EMA_2+1)))          
    
    for i, row in data.iterrows():
        if i==0:
            data["ST_BUY_SELL"]="NA"
        elif (data.loc[i,"ST"]<data.loc[i,"close"]) :
            data.loc[i,"ST_BUY_SELL"]="BUY"
            data.loc[i,"SL"]=data.loc[i,"sma_50"]-1.5
        else:
            data.loc[i,"ST_BUY_SELL"]="SELL"
            data.loc[i,"SL"]=data.loc[i,"sma_50"]+1.5
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"adx_20"]="NO"
        elif (data.loc[i,"adxr"]>20) & (data.loc[i,"adxr"]>data.loc[i-1,"adxr"]) & (data.loc[i-1,"adxr"]>data.loc[i-2,"adxr"]):
            data.loc[i,"adx_20"]="YES"
        else:
            data.loc[i,"adx_20"]="NO"
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"macd_buy_sell"]="NO"
        elif (data.loc[i,"macds"]>data.loc[i-1,"macds"]) & (data.loc[i,"macd"]>data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="BUY"
        elif (data.loc[i,"macds"]<data.loc[i-1,"macds"]) & (data.loc[i,"macd"]<data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="SELL"    
    data["PP"]=round((data[["high","low","close"]].sum(axis=1))/3,1).shift()
    data["R1"]=round((data["PP"]*2)-(data["low"]).shift(),1)
    data["R2"]=round(data["PP"]+(data["high"]-data["low"]).shift(),1)
    data["R3"]=round((data["high"]).shift()+(2*(data["PP"]-(data["low"].shift()))),1)
    data["S1"]=round((2*data["PP"])-(data["high"]).shift(),1)
    data["S2"]=round(data["PP"]-(data["high"]-data["low"]).shift(),1)
    data["S3"]=round((data["low"]).shift()-2*((data["high"]).shift()-data["PP"]),1)
    data=round(data,1)
    SuperTrend=data.iloc[75:]#[["ST_BUY_SELL","Close","ST"]]#.tail(1)
    data=data[['Datetime', 'open', 'high', 'low', 'close', 'boll', 'boll_ub', 'boll_lb','adx',
       'adxr', 'sma_50', 'ST','ST_BUY_SELL', 'adx_20', 'ema_5', 'ema_20',"SL","macd_buy_sell",'PP', 'R1', 'R2',
       'R3', 'S1', 'S2', 'S3']]
    data=round(data.reset_index(inplace=False).drop(["index"],axis=1),1) 
    return(data)    


def Stratergy_one(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA):
    global SuperTrend
    try:
        data =yf.download(Stock_name+".NS", period="5d",interval="5m",progress=False)
    except:
        pass
    data.columns=["open","high","low","close","amount","volume"]
    data=StockDataFrame(data)
    data.get('boll')
    data.get('adx')
    data.get("macd")
    data=data.assign(Symbol=Stock_name)
    data=pd.DataFrame(data)
    data=data.reset_index()
    data=data.assign(sma_value=data["close"].rolling(SMA).mean())
    data=data.assign(BUY_SELL='NA')
    for i, row in data.iterrows():
        if i<=2:
            data.loc[i,"sma_status"]="NA"
        elif (data.loc[i,"sma_value"]>data.loc[i-1,"sma_value"])&(data.loc[i-1,"sma_value"]>data.loc[i-2,"sma_value"]):
            data.loc[i,"sma_status"]="INC"
        elif (data.loc[i,"sma_value"]<data.loc[i-1,"sma_value"])&(data.loc[i-1,"sma_value"]<data.loc[i-2,"sma_value"]):
            data.loc[i,"sma_status"]="DEC"
        else:
            data.loc[i,"sma_status"]="NA"
    data=data.assign(tr0 = abs(data["high"] - data["low"]))
    data=data.assign(tr1 = abs(data["high"] - data["close"].shift(1)))
    data=data.assign(tr2= abs(data["low"]- data["close"].shift(1)))
    data=data.assign(TR = round(data[['tr0', 'tr1', 'tr2']].max(axis=1),2))
    
    # data["ATR"]=0.00
    data=data.assign(BUB=0.00)
    data=data.assign(BLB=0.00)
    data=data.assign(FUB=0.00)
    data=data.assign(FLB=0.00)
    data=data.assign(ST=0.00)
    data=data.assign(ATR=data["TR"].rolling(Supertrend_period).mean())
    data=data.assign(ATR= data["ATR"].replace('nan', np.nan).fillna(0))                                      
    data=data.assign(BUB= round(((data["high"] + data["low"]) / 2) + (Supertrend_length * data["ATR"]),2))
    data=data.assign(BLB= round(((data["high"] + data["low"]) / 2) - (Supertrend_length * data["ATR"]),2))
    data=data.assign(FUB = data["FUB"].replace('nan', np.nan).fillna(0))

    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FUB"]=0.00
        else:
            if (data.loc[i,"BUB"]<data.loc[i-1,"FUB"])|(data.loc[i-1,"close"]>data.loc[i-1,"FUB"]):
                data.loc[i,"FUB"]=data.loc[i,"BUB"]
            else:
                data.loc[i,"FUB"]=data.loc[i-1,"FUB"]
    
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"FLB"]=0.00
        else:
            if (data.loc[i,"BLB"]>data.loc[i-1,"FLB"])|(data.loc[i-1,"close"]<data.loc[i-1,"FLB"]):
                data.loc[i,"FLB"]=data.loc[i,"BLB"]
            else:
                data.loc[i,"FLB"]=data.loc[i-1,"FLB"]               
    for i, row in data.iterrows():
        if i==0:
            data.loc[i,"ST"]=0.00
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"]) & (data.loc[i,"close"]<=data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FUB"])&(data.loc[i,"close"]>data.loc[i,"FUB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]>=data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FLB"]
        elif (data.loc[i-1,"ST"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]<data.loc[i,"FLB"]):
            data.loc[i,"ST"]=data.loc[i,"FUB"]

    for i, row in data.iterrows():
       if i<=2:
           data.loc[i,"ema_1"]=0.00
           data.loc[i,"ema_2"]=0.00
       else:
           data.loc[i,"ema_1"]=data.loc[i,"close"]*(2/(EMA_1+1))+data.loc[i-1,"ema_1"]*(1-(2/(EMA_1+1)))
           data.loc[i,"ema_2"]=data.loc[i,"close"]*(2/(EMA_2+1))+data.loc[i-1,"ema_2"]*(1-(2/(EMA_2+1)))          
    
    for i, row in data.iterrows():
        if i==0:
            data["ST_BUY_SELL"]="NA"
        elif (data.loc[i,"ST"]<data.loc[i,"close"]) :
            data.loc[i,"ST_BUY_SELL"]="BUY"
            data.loc[i,"SL"]=data.loc[i,"sma_value"]-1.5
        else:
            data.loc[i,"ST_BUY_SELL"]="SELL"
            data.loc[i,"SL"]=data.loc[i,"sma_value"]+1.5

    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"ADX_STATUS"]="NA"
        elif (data.loc[i,"adxr"]>20) & (data.loc[i,"adxr"]>data.loc[i-1,"adxr"]) & (data.loc[i-1,"adxr"]>data.loc[i-2,"adxr"]):
            data.loc[i,"ADX_STATUS"]="YES"
        else:
            data.loc[i,"ADX_STATUS"]="NA"
    '''
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"macd_buy_sell"]="NA"
        elif (data.loc[i,"macds"]>data.loc[i-1,"macds"]) & (data.loc[i,"macd"]>data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="BUY"
        elif (data.loc[i,"macds"]<data.loc[i-1,"macds"]) & (data.loc[i,"macd"]<data.loc[i,"macds"]):
            data.loc[i,"macd_buy_sell"]="SELL"  
        else:
            data.loc[i,"macd_buy_sell"]=data.loc[i-1,"macd_buy_sell"]
    '''
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"macd_buy_sell"]="NA"
        elif (data.loc[i,"macd"]>data.loc[i-2:i-1,"macd"]).all():
            data.loc[i,"macd_buy_sell"]="BUY"
        elif (data.loc[i,"macd"]<data.loc[i-2:i-1,"macd"]).all():
            data.loc[i,"macd_buy_sell"]="SELL" 
        else:
            data.loc[i,"macd_buy_sell"]=data.loc[i-1,"macd_buy_sell"]

    for i, row in data.iterrows():
        if (i<3) & (str(data.loc[i,'Datetime'])[11:]=='09:15:00+05:30'):
            data.loc[i,"TP"]=data.loc[i,'volume']
            data.loc[i,"VWAP"]=data.loc[i,'close']
            j=i
        elif (str(data.loc[i,'Datetime'])[11:]=='09:15:00+05:30'):
            #print(i,j,data.loc[i,'Datetime'])#,data.iloc[j:6])
            data.loc[i,"TP"]=((data.loc[i,'close']+data.loc[i,'high']+data.loc[i,'low'])/3)*data.loc[i,'volume']
            data.loc[i,"VWAP"]=(data.iloc[j:i+1,7].sum()/data.iloc[j:i+1,6].sum())
            j=i
        else:
            
            data.loc[i,"TP"]=((data.loc[i,'close']+data.loc[i,'high']+data.loc[i,'low'])/3)*data.loc[i,'volume']
            data.loc[i,"VWAP"]=(data.iloc[j:i+1,36].sum()/data.iloc[j:i+1,6].sum())
            #print(data.loc[i,'Datetime'],data.loc[i,'Symbol'],data.loc[i,'TP'],data.loc[i,'VWAP'],data.iloc[j:i,36].sum())   
    for i, row in data.iterrows():
        if i<1:
            pass
        elif (data.loc[i,"close"]-((data.loc[i,'close']*0.0)/100))>data.loc[i,"VWAP"]: #
            data.loc[i,"VWAP_CO"]="VWAP_BUY"
        elif (data.loc[i,"close"]+((data.loc[i,'close']*0.0)/100))<data.loc[i,"VWAP"]: #
            data.loc[i,"VWAP_CO"]="VWAP_SELL"
        else:
            data.loc[i,"VWAP_CO"]="NO_CO"
    data=round(data,1)
    data=data.iloc[75:]#[["ST_BUY_SELL","Close","ST"]]#.tail(1)
    #print(data)
    #print(data[['Datetime', 'open', 'high', 'low', 'close', 'amount', 'volume','TP','macd_buy_sell', 'VWAP','VWAP_CO']])
    #data=data[['Datetime', 'open', 'high', 'low', 'close', 'amount', 'volume',
    #   'Symbol','ST','ST_BUY_SELL','ema_1', 'ema_2', 'sma_value','sma_status', 'SL',
    #    'macds','macd_buy_sell',"BUY_SELL","VWAP","VWAP_CO"]]
    #data.columns=['Datetime', 'open', 'high', 'low', 'close', 'amount', 'volume',
    #       'Symbol','ST_Line','ST_BUY_SELL', 'EMA_1', 'EMA_2','SMA', 'SMA_Status','SMA_SL',
    #       "MACDS","MACD_BUY_SELL","BUY_SELL",'VWAP',"VWAP_CO"]
    tickers = Ticker(Stock_name+".NS")
    prices= tickers.price
    LTP_PRICE=prices[Stock_name+".NS"]["regularMarketPrice"]
    data=data.reset_index(drop=True)
    '''
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"BUY_SELL"]="NA"
        elif (data.loc[i,'ST_BUY_SELL']=="BUY") & (data.loc[i-1,'ST_BUY_SELL']=="SELL") & (data.loc[i-2,'ST_BUY_SELL']=="SELL") & (data.loc[i-3,'ST_BUY_SELL']=="SELL") & (data.loc[i-4,'ST_BUY_SELL']=="SELL") & (data.loc[i,'EMA_1']>data.loc[i,'EMA_2']) & (data.loc[i,'SMA']<data.loc[i,'EMA_1']) & (data.loc[i,'SMA']<data.loc[i,'EMA_2']) & (data.loc[i,'SMA_Status']=="INC"):
            #print(data.loc[i-1,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="BUY"
        elif (data.loc[i,'ST_BUY_SELL']=="SELL") & (data.loc[i-1,'ST_BUY_SELL']=="BUY") & (data.loc[i-2,'ST_BUY_SELL']=="BUY") & (data.loc[i-3,'ST_BUY_SELL']=="BUY") & (data.loc[i-4,'ST_BUY_SELL']=="BUY") & (data.loc[i,'EMA_1']<data.loc[i,'EMA_2']) & (data.loc[i,'SMA']>data.loc[i,'EMA_1']) & (data.loc[i,'SMA']>data.loc[i,'EMA_2']) & (data.loc[i,'SMA_Status']=="DEC"):
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="SELL"
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"BUY_SELL"]="NA"
        elif (data.loc[i,'ST_BUY_SELL']=="BUY") & (data.loc[i-1,'ST_BUY_SELL']=="SELL") & (data.loc[i-2,'ST_BUY_SELL']=="SELL") & (data.loc[i-3,'ST_BUY_SELL']=="SELL") & (data.loc[i-4,'ST_BUY_SELL']=="SELL") & (data.loc[i,'MACDS']<-1) & (data.loc[i,'SMA_Status']=="INC"):
            #print(data.loc[i-1,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="BUY"
        elif (data.loc[i,'ST_BUY_SELL']=="SELL") & (data.loc[i-1,'ST_BUY_SELL']=="BUY") & (data.loc[i-2,'ST_BUY_SELL']=="BUY") & (data.loc[i-3,'ST_BUY_SELL']=="BUY") & (data.loc[i-4,'ST_BUY_SELL']=="BUY") & (data.loc[i,'MACDS']>1) & (data.loc[i,'SMA_Status']=="DEC"):
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="SELL"    
    
    for i, row in data.iterrows():
        if i<4:
            data.loc[i,"BUY_SELL"]="NA"
            #print(data.columns)
            #break
        elif (data.loc[i,'ST_BUY_SELL']=="BUY") & (data.loc[i,'MACDS']<-macd_alignment(data.loc[i,'open'])) & (data.loc[i-2,'MACDS']>data.loc[i,'MACDS']) & (data.loc[i,'VWAP']<LTP_PRICE):
            #print(data.loc[i-1,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="BUY"
        elif (data.loc[i,'ST_BUY_SELL']=="SELL") & (data.loc[i,'MACDS']>macd_alignment(data.loc[i,'open'])) & (data.loc[i-2,'MACDS']<data.loc[i,'MACDS']) & (data.loc[i,'VWAP']>LTP_PRICE):
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="SELL"          
    '''
    for i, row in data.iterrows():
        if i<5:
            data.loc[i,"BUY_SELL"]="NA"             
            #print(data.columns)
            #break
        elif (data.loc[i-3,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-2,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-4,'macd_buy_sell']=='SELL') & (data.loc[i-3,'macd_buy_sell']=='SELL') & ((data.loc[i-2,'macd_buy_sell']=='BUY') | (data.loc[i-1,'macd_buy_sell']=='BUY')) : # & (data.loc[i,'MACDS']<-macd_alignment(data.loc[i,'close'])):
            data.loc[i,"BUY_SELL"]="BUY"
        elif (data.loc[i-3,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-2,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-4,'macd_buy_sell']=='BUY') & (data.loc[i-3,'macd_buy_sell']=='BUY') & ((data.loc[i-2,'macd_buy_sell']=='SELL') | (data.loc[i-1,'macd_buy_sell']=='SELL')) : #& (data.loc[i,'MACDS']>macd_alignment(data.loc[i,'close'])) : 
            data.loc[i,"BUY_SELL"]="SELL"  
        elif (data.loc[i-1,'close']<data.loc[i-4:i-1,'boll_lb']).any() & (data.loc[i,'macdh']<-macd_alignment(data.loc[i,'macd'])):
            data.loc[i,"BUY_SELL"]="S4_BUY"
        elif (data.loc[i-1,'close']>data.loc[i-4:i-1,'boll_ub']).any() & (data.loc[i,'macds']>macd_alignment(data.loc[i,'macd'])):
            data.loc[i,"BUY_SELL"]="S4_SELL"
        elif (data.loc[i-2:i-1,'macd_buy_sell']=='SELL').all() & (data.loc[i,'macd_buy_sell']=='BUY') & (data.loc[i,'macdh']<-macd_alignment(data.loc[i,'macd'])):# & (data.loc[i-1,'VWAP_CO']=='VWAP_BUY'):
            data.loc[i,"BUY_SELL"]="S5_BUY"
        elif (data.loc[i-2:i-1,'macd_buy_sell']=='BUY').all() & (data.loc[i,'macd_buy_sell']=='SELL') & (data.loc[i,'macds']>macd_alignment(data.loc[i,'macd'])): # & (data.loc[i-1,'VWAP_CO']=='VWAP_SELL'):
            data.loc[i,"BUY_SELL"]="S5_SELL"            
        '''elif (data.loc[i-3,'ST_BUY_SELL']=='SELL') & (data.loc[i-2,'ST_BUY_SELL']=='SELL') & (data.loc[i-1,'ST_BUY_SELL']=='BUY') & (data.loc[i-4,'macd_buy_sell']=='SELL') & (data.loc[i-3,'macd_buy_sell']=='SELL') & ((data.loc[i-2,'macd_buy_sell']=='BUY') | (data.loc[i-1,'macd_buy_sell']=='BUY')) & ((data.loc[i-4,'VWAP_CO']=='VWAP_SELL') | (data.loc[i-3,'VWAP_CO']=='VWAP_SELL') | (data.loc[i-2,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'VWAP_CO']=='VWAP_BUY')) & (data.loc[i-1,'macd']<-macd_alignment(data.loc[i-1,'close'])): # :
            data.loc[i,"BUY_SELL"]="S1_BUY"
        elif (data.loc[i-3,'ST_BUY_SELL']=='BUY') & (data.loc[i-2,'ST_BUY_SELL']=='BUY') & (data.loc[i-1,'ST_BUY_SELL']=='SELL') & (data.loc[i-4,'macd_buy_sell']=='BUY') & (data.loc[i-3,'macd_buy_sell']=='BUY') & ((data.loc[i-2,'macd_buy_sell']=='SELL') | (data.loc[i-1,'macd_buy_sell']=='SELL')) & ((data.loc[i-4,'VWAP_CO']=='VWAP_BUY') | (data.loc[i-3,'VWAP_CO']=='VWAP_BUY') | (data.loc[i-2,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'VWAP_CO']=='VWAP_SELL')) & (data.loc[i-1,'macd']>macd_alignment(data.loc[i-1,'close'])): # : 
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="S1_SELL" 
        elif (data.loc[i-3,'ST_BUY_SELL']=='SELL') & (data.loc[i-2,'ST_BUY_SELL']=='SELL') & (data.loc[i-1,'ST_BUY_SELL']=='BUY') & (data.loc[i-4,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-3,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'macd']<3):
            data.loc[i,"BUY_SELL"]="S2_BUY"
        elif (data.loc[i-3,'ST_BUY_SELL']=='BUY') & (data.loc[i-2,'ST_BUY_SELL']=='BUY') & (data.loc[i-1,'ST_BUY_SELL']=='SELL') & (data.loc[i-4,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-3,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'macd']>3): # : 
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="S2_SELL"
        elif (data.loc[i-3,'ST_BUY_SELL']=='SELL') & (data.loc[i-2,'ST_BUY_SELL']=='SELL') & (data.loc[i-1,'ST_BUY_SELL']=='BUY') & (data.loc[i-4,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-3,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'macd']<3):
            data.loc[i,"BUY_SELL"]="S2_BUY"
        elif (data.loc[i-3,'ST_BUY_SELL']=='BUY') & (data.loc[i-2,'ST_BUY_SELL']=='BUY') & (data.loc[i-1,'ST_BUY_SELL']=='SELL') & (data.loc[i-4,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-3,'VWAP_CO']=='VWAP_BUY') & (data.loc[i-1,'VWAP_CO']=='VWAP_SELL') & (data.loc[i-1,'macd']>3): # : 
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="S2_SELL"
        elif (data.loc[i-3:i-2,'ST_BUY_SELL']=='SELL').any()  & (data.loc[i-1:i,'ST_BUY_SELL']=='BUY').all() & (data.loc[i-3:i-2,'VWAP_CO']=='VWAP_SELL').any()  & (data.loc[i-1:i,'VWAP_CO']=='VWAP_BUY').all() & (data.loc[i,'macdh']<-macd_alignment(data.loc[i,'macd'])):
            data.loc[i,"BUY_SELL"]="S3_BUY"
        elif (data.loc[i-3:i-2,'ST_BUY_SELL']=='BUY').any()  & (data.loc[i-1:i,'ST_BUY_SELL']=='SELL').all() & (data.loc[i-3:i-2,'VWAP_CO']=='VWAP_BUY').any()  & (data.loc[i-1:i,'VWAP_CO']=='VWAP_SELL').all() & (data.loc[i,'macds']>macd_alignment(data.loc[i,'macd'])):
            #print(data.loc[i-2,'ST_BUY_SELL'])
            data.loc[i,"BUY_SELL"]="S3_SELL" '''    
    return(data)
    
#Stratergy_one('SBI',48,3,50,100,50)
#print(yf.download("SBI"))
#Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA='TITAN',48,3,20,50,50
#data=Stratergy_one(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA)[1]
#data=yf.download("HAVELLS.NS", period="5d",interval="5m",progress=False)
#print(data[data.Datetime>='2024-07-01'])
#data.columns=["open","high","low","close","amount","volume"]
#data=StockDataFrame(data)
#data=data.round(2).reset_index()
#for i, row in data.iterrows():
#    if (i<3) & (str(data.loc[i,'Datetime'])[11:]=='09:15:00+05:30'):
#        data.loc[i,"TP"]=data.loc[i,'volume']
#        j=i
#    elif (str(data.loc[i,'Datetime'])[11:]=='09:15:00+05:30'):
        #print(i,j,data.loc[i,'Datetime'])#,data.iloc[j:6])
#        data.loc[i,"TP"]=((data.loc[i,'close']+data.loc[i,'high']+data.loc[i,'low'])/3)*data.loc[i,'volume']
#        data.loc[i,"CUMV"]=data.iloc[j:i+1,7].sum()/data.iloc[j:i+1,6].sum()
#        j=i
#    else:
        #print(data.iloc[j:i,6].sum())
#       data.loc[i,"TP"]=((data.loc[i,'close']+data.loc[i,'high']+data.loc[i,'low'])/3)*data.loc[i,'volume']
#        data.loc[i,"CUMV"]=data.iloc[j:i+1,7].sum()/data.iloc[j:i+1,6].sum()



#data.get('macd')

 
#print(data.tail(76))    


#print(data.head(),j)
#print(data[data.BUY_SELL=='BUY'])
#print(data[data.BUY_SELL=='SELL'])
#print(data[data.BUY_SELL=='NO'])
#print(Stock_name,Supertrend_period,Supertrend_length,EMA_1,EMA_2,SMA)
#print(yf.download(Stock_name+".NS", period="1mo",interval="5m",progress=False))

msg_rep=[]
def run():    
    global msg_rep
    #try:
    NSE_NS=['ACC.NS','ADANIPORTS.NS','APOLLOHOSP.NS','ASIANPAINT.NS','AUROPHARMA.NS','AXISBANK.NS',
            'BALKRISIND.NS','BANDHANBNK.NS','BATAINDIA.NS','BERGEPAINT.NS','BHARATFORG.NS','BHARTIARTL.NS','BIOCON.NS','BPCL.NS',
            'CENTURYTEX.NS','CIPLA.NS','COLPAL.NS','CONCOR.NS','CUMMINSIND.NS',
            'DABUR.NS','ESCORTS.NS','GLENMARK.NS','GODREJCP.NS','GODREJPROP.NS','GRASIM.NS',
            'HAVELLS.NS','HCLTECH.NS','HDFCBANK.NS','HDFCLIFE.NS','HINDPETRO.NS','IBULHSGFIN.NS',
            'ICICIBANK.NS','ICICIPRULI.NS','IGL.NS','INDIGO.NS','INDUSINDBK.NS','INFY.NS','JUBLFOOD.NS',
            'JUSTDIAL.NS','KOTAKBANK.NS','LICHSGFIN.NS','LT.NS','LUPIN.NS',
            'MARICO.NS','MFSL.NS','MGL.NS','MUTHOOTFIN.NS',
            'PEL.NS','PETRONET.NS','PIDILITIND.NS','RAMCOCEM.NS','RELIANCE.NS',
            'SBILIFE.NS','SIEMENS.NS','SUNPHARMA.NS','SUNTV.NS',
            'TATACHEM.NS','TATACONSUM.NS','TATASTEEL.NS','TECHM.NS','TITAN.NS','TORNTPOWER.NS','TVSMOTOR.NS',
            'UBL.NS','UPL.NS','VOLTAS.NS','WIPRO.NS']
    NSE_STOCK=['ACC','ADANIPORTS','APOLLOHOSP','ASIANPAINT','AUROPHARMA','AXISBANK',
                'BALKRISIND','BANDHANBNK','BATAINDIA','BERGEPAINT','BHARATFORG','BHARTIARTL','BIOCON','BPCL',
                'CENTURYTEX','CIPLA','COLPAL','CONCOR','CUMMINSIND',
                'DABUR','ESCORTS','GLENMARK','GODREJCP','GODREJPROP','GRASIM',
                'HAVELLS','HCLTECH','HDFCBANK','HDFCLIFE','HINDPETRO','IBULHSGFIN',
                'ICICIBANK','ICICIPRULI','IGL','INDIGO','INDUSINDBK','INFY',
                'JUBLFOOD','JUSTDIAL','KOTAKBANK','LICHSGFIN','LT','LUPIN',
                'MARICO','MFSL','MGL','MUTHOOTFIN',
                'PEL','PETRONET','PIDILITIND','RAMCOCEM','RELIANCE',
                'SBILIFE','SIEMENS','SUNPHARMA','SUNTV',
                'TATACHEM','TATACONSUM','TATASTEEL','TECHM','TITAN','TORNTPOWER','TVSMOTOR',
                'UBL','UPL','VOLTAS','WIPRO']
    NSE_TOKEN=[22,15083,157,236,275,5900,335,2263,371,404,422,10604,11373,526,7929,625,694,15141,4749,1901,772,958,7406,10099,17875,1232,9819,7229,1330,1333,467,1406,30125,4963,18652,11262,11195,5258,29135,1594,18096,29962,1922,1997,11483,10440,4067,10447,2142,17534,14356,23650,11543,2412,11351,2664,13147,2043,2885,21808,3150,4306,3351,13404,3405,3432,3499,13538,3506,13786,8479,16713,17069,11287,3718,3787]
                #    "token_no":NSE_TOKEN,
    NSE_STOCK_DATA={"symbols":NSE_STOCK,
                    "symbol.NS":NSE_NS}
    ns_stock_token=pd.DataFrame(NSE_STOCK_DATA)
    #ns_stock_token["token_no"]=ns_stock_token["token_no"].astype(int)
    ns_stock_token=ns_stock_token.assign(Qty=10)
    start_date=str(date.today()) #str(date.today()-timedelta(days=2))
    
    for i, row in ns_stock_token.iterrows():
        value = row['symbols']
        clearline("Pls wait... validating",value)
        data=Stratergy_one(value,48,3,20,50,100)
        #data=output[1]
        #data2=output[0]
        #print(data)
        #break
        if ((data['BUY_SELL']=='BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            #print(result)
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)
                #print(msg)
        if ((data['BUY_SELL']=='S1_BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='S1_SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='S1_BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='S1_SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'STRATERGY S1 On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        #print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)
        if ((data['BUY_SELL']=='S2_BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='S2_SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='S2_BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='S2_SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'STRATERGY S2 On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        #print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)
        if ((data['BUY_SELL']=='S3_BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='S3_SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='S3_BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='S3_SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'STRATERGY S3 On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        #print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)
        if ((data['BUY_SELL']=='S4_BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='S4_SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='S4_BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='S4_SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'STRATERGY S4 On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)
        if ((data['BUY_SELL']=='S5_BUY').any() & (data['Datetime']>=start_date).any()) | ((data['BUY_SELL']=='S5_SELL').any() & (data['Datetime']>=start_date).any()) :
            result=data[((data.BUY_SELL=='S5_BUY') & (data['Datetime']>=start_date)) | ((data.BUY_SELL=='S5_SELL') & (data['Datetime']>=start_date))]
            result=result.reset_index()
            if len(result)>0:
                for j, row in result.iterrows():
                    msg= 'STRATERGY S5 On '+str(result.loc[j,'Datetime'])+' '+result.loc[j,'BUY_SELL']+' '+str(result.loc[j,'Symbol'])+ ' at ' +str(result.loc[j,'close'])
                    if msg not in msg_rep:
                        print(msg)
                        #twlio (msg,'+919944333650')
                        msg_rep.append(msg)                
                #print(result[['Datetime','Symbol', 'open', 'high', 'low', 'close','ST_BUY_SELL','EMA_1', 'EMA_2', 'SMA', 'SMA_SL','MACD_SIGNAL','MACDS','BUY_SELL']])
       
    #print(msg_rep)

    '''
        if ((data2['BUY_SELL']=='BUY').any() & (data2['Datetime']>=start_date).any()) | ((data2['BUY_SELL']=='SELL').any() & (data2['Datetime']>=start_date).any()) :
            vwap_result=data2[((data2.BUY_SELL=='BUY') & (data2['Datetime']>=start_date)) | ((data2.BUY_SELL=='SELL') & (data2['Datetime']>=start_date))]
            vwap_result=vwap_result.reset_index()
            for j, row in vwap_result.iterrows():
               msg= 'At '+str(vwap_result.loc[j,'Datetime'])+' '+vwap_result.loc[j,'BUY_SELL']+' '+str(vwap_result.loc[j,'Symbol'])+ ' at ' +str(vwap_result.loc[j,'LTP']) 
               twlio (msg,'+919944333650')
               print(msg)
    '''      
    run()
        


#run()
#msg='On 2024-07-03 09:20:00+05:30 BUY BALKRISIND at 41'
#for i in msg_rep:
#    if i.__contains__(msg):
#        print(i)
#    elif msg not in msg_rep:
#        print(i)